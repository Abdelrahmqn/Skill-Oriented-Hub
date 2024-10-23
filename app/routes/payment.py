import logging
import requests
from os import getenv
from flask import Blueprint, request, render_template, flash, redirect, url_for, session, jsonify
from flask_login import login_required, current_user
from ..models import Course, Enrollment
from .. import db

bp = Blueprint('payment', __name__)

@bp.route('/pay/<int:course_id>', methods=['POST'])
@login_required
def init_payment(course_id):
    course = Course.query.get_or_404(course_id)
    return render_template("payment/payment.html", course_id=course_id, price=course.price)

@bp.route("/payments/<order_id>/capture", methods=["POST"])
@login_required
def capture_payment(order_id):
    # Capture the payment
    captured_payment = approve_payment(order_id)

    # Check if the payment was successful
    if captured_payment['status'] == 'COMPLETED':
        # Enroll the student in the course
        flash('Course created successfully!', 'success')
        course_id = request.json.get('course_id')  # Get course_id from the request
        enrollment = Enrollment(student_id=current_user.id, course_id=course_id)
        # Add the enrollment to the database
        db.session.add(enrollment)
        db.session.commit()
        flash('You have been successfully enrolled the course.', 'success')
        # Redirect to the course detail page after successful payment
        return redirect(url_for('payment.payment_success', order_id=order_id))  # Update this line with the correct route name for course details
    else:
        return jsonify({"error": "Payment not completed."}), 400

@bp.route('/payment/success/<order_id>')
@login_required
def payment_success(order_id):
    return render_template('payment/payment_success.html', order_id=order_id)

def approve_payment(order_id):
    api_link = f"https://api-m.sandbox.paypal.com/v2/checkout/orders/{order_id}/capture"
    client_id = getenv("PAYPAL_CLIENT_ID")
    secret = getenv("PAYPAL_SECRET")
    access_token = get_paypal_access_token(client_id, secret)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.post(url=api_link, headers=headers)
    response.raise_for_status()  # Raises an exception for HTTP errors
    return response.json()

def get_paypal_access_token(client_id, secret):
    auth_url = "https://api-m.sandbox.paypal.com/v1/oauth2/token"

    headers = {
        "Accept": "application/json",
        "Accept-Language": "en_US"
    }

    auth_response = requests.post(auth_url, headers=headers, auth=(client_id, secret), data={"grant_type": "client_credentials"})
    auth_response.raise_for_status()  # Raises an exception for HTTP errors

    token_data = auth_response.json()
    return token_data['access_token']
