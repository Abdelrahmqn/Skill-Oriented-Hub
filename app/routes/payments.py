import requests
from os import getenv
from flask import Blueprint
from flask import request, render_template, flash, redirect, url_for, session
from flask_login import login_required
from ..models import Course, Enrollment
from .. import db

bp = Blueprint('payment', __name__)

# create a function to initiate and handle responses.
def create_payment_order(amount, currency='USD'):
    try:
        response = requests.post(
            f"{getenv('PAYMOB_ENDPOINT')}/orders",
            json={
                "amount": amount * 100,
                "currency": currency,
                "integration_id": getenv('PAYMOB_INTEGRATION_ID')
            },
            headers={
                'Authorization': f"Bearer {getenv('PAYMOB_API_KEY')}",  # Corrected header format
                'Content-Type': 'application/json'
            }
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Payment error: {e}")
        return {"error": "Payment request failed"}


@bp.route('/pay/<int:course_id>', methods=['POST'])
@login_required
def init_payment(course_id):
    course = Course.query.get_or_404(course_id)

    # Create a payment order via Paymob
    order = create_payment_order(course.price, currency='USD')
    
    if order.get('id'):
        # Store the order ID temporarily for tracking (you can use session)
        session['order_id'] = order['id']

        # Generate payment link using Paymob's iframe URL (replace with actual format)
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

    if data.get('success') and data.get('obj', {}).get('amount_cents'):
        user_id = data['obj']['metadata']['user_id']
        course_id = data['obj']['metadata']['course_id']

        enrollment = Enrollment(student_id=user_id, course_id=course_id)
        db.session.add(enrollment)
        db.session.commit()

        flash('Payment successful! You are now enrolled in the course.', 'success')
    else:
        flash('Payment failed or was canceled.', 'danger')

    return redirect(url_for('course.list_courses'))