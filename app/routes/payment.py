import requests
from os import getenv
from flask import Blueprint, request, render_template, flash, redirect, url_for, session
from flask_login import login_required
from ..models import Course, Enrollment
from .. import db
import logging

# Setup logging
logger = logging.getLogger()

# Paymob API configuration
PAYMOB_ENDPOINT = 'https://accept.paymob.com/api/'
bp = Blueprint('payment', __name__)

def create_payment_order(amount, currency='EGP'):
    """Initiate a payment order with Paymob."""
    logger.debug(f"Paymob Endpoint: {getenv('PAYMOB_ENDPOINT')}")
    logger.debug(f"Paymob API Key: {getenv('PAYMOB_API_KEY')}")

    payload = {
        "amount_cents": int(amount * 100),  # Ensure this is an integer
        "currency": currency,
        "delivery_needed": False,
        "items": [],
        "metadata": {
            "user_id": session.get('user_id'),
            "course_id": session.get('course_id')
        }
    }
    headers = {
        'Authorization': f"Bearer {getenv('PAYMOB_API_KEY')}",
        'Content-Type': 'application/json'
    }

    logger.debug(f"Order Request Payload: {payload}")

    try:
        response = requests.post(f"{getenv('PAYMOB_ENDPOINT')}/ecommerce/orders", json=payload, headers=headers)
        logger.debug(f"Order Response: {response.status_code} - {response.text}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Order creation failed: {e}")
        if response is not None:
            logger.error(f"Response Content: {response.status_code} - {response.text}")
            logger.error(f"Response Headers: {response.headers}")  # Log response headers
        else:
            logger.error("No response received.")
        return {"error": str(e)}


@bp.route('/pay/<int:course_id>', methods=['POST'])
@login_required
def init_payment(course_id):
    course = Course.query.get_or_404(course_id)

    # Store the course ID and user ID in the session
    session['course_id'] = course.id
    session['user_id'] = session.get('user_id')

    # Create a payment order via Paymob
    order = create_payment_order(course.price, currency='EGP')

    if order.get('id'):
        # Store the order ID temporarily for tracking
        session['order_id'] = order['id']

        # Generate payment link using Paymob's iframe URL
        payment_url = f"https://accept.paymob.com/api/acceptance/iframes/{getenv('PAYMOB_IFRAME_ID')}?payment_token={order['token']}"

        # Redirect the user to Paymob's payment page
        return redirect(payment_url)
    else:
        flash('Payment initiation failed. Please try again.', 'danger')
        return redirect(url_for('course.course_details', course_id=course.id))

@bp.route('/purchase_unavailable')
def purchase_unavailable():
    flash('Course purchase is currently unavailable. Please check back later.', 'info')
    return render_template('purchase_unavailable.html')

@bp.route('/payment_callback', methods=['POST'])
def payment_callback():
    data = request.json

    # Verify payment success and required fields
    if data.get('success') and data.get('obj', {}).get('amount_cents'):
        user_id = data['obj']['metadata'].get('user_id')
        course_id = data['obj']['metadata'].get('course_id')

        # Check if enrollment already exists to avoid duplication
        if not Enrollment.query.filter_by(student_id=user_id, course_id=course_id).first():
            enrollment = Enrollment(student_id=user_id, course_id=course_id)
            db.session.add(enrollment)
            db.session.commit()
            flash('Payment successful! You are now enrolled.', 'success')
        else:
            flash('You are already enrolled in this course.', 'info')
    else:
        flash('Payment failed or canceled.', 'danger')

    return redirect(url_for('course.list_courses'))
