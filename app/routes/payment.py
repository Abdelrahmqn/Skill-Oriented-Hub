import requests
from os import getenv
from flask import Blueprint, request, render_template, flash, redirect, url_for, session
from flask_login import login_required
from ..models import Course, Enrollment
from .. import db

bp = Blueprint('payment', __name__)

# Create a function to initiate and handle responses.
def create_payment_order(amount, currency='USD'):
    try:
        response = requests.post(
            f"{getenv('PAYMOB_ENDPOINT')}/api/ecommerce/orders",  # Make sure endpoint is correct
            json={
                "amount_cents": amount * 100,  # Amount is converted to cents
                "currency": currency,
                "integration_id": getenv('PAYMOB_INTEGRATION_ID'),
                "merchant_order": {
                    "metadata": {
                        "user_id": session.get('user_id'),
                        "course_id": session.get('course_id')
                    }
                }
            },
            headers={
                'Authorization': f"Bearer {getenv('PAYMOB_API_KEY')}",
                'Content-Type': 'application/json'
            }
        )

        return response.json()
    except requests.RequestException as e:
        print(f"Payment error: {e}")
        return {"error": "Payment request failed"}

@bp.route('/pay/<int:course_id>', methods=['POST'])
@login_required
def init_payment(course_id):
    course = Course.query.get_or_404(course_id)

    # Store the course ID in the session for later use in payment callback
    session['course_id'] = course.id
    session['user_id'] = session.get('user_id')

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

    # Check for a successful payment response
    if data.get('success') and data.get('obj', {}).get('amount_cents'):
        user_id = data['obj']['metadata']['user_id']
        course_id = data['obj']['metadata']['course_id']

        # Create enrollment if payment was successful
        enrollment = Enrollment(student_id=user_id, course_id=course_id)
        db.session.add(enrollment)
        db.session.commit()

        flash('Payment successful! You are now enrolled in the course.', 'success')
    else:
        flash('Payment failed or was canceled.', 'danger')

    return redirect(url_for('course.list_courses'))
