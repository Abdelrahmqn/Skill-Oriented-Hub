import stripe
from flask import Blueprint, redirect, url_for, flash, request, render_template
from flask_login import login_required, current_user
from app.models import Payment, db

stripe.api_key = 'my_secretttt_keeyyy!!'

bp = Blueprint('payments', __name__, url_prefix='/payment')

@bp.route('checkout/<int:course_id>', methods=['POST'])
@login_required
def checkout(course_id):
    course = Course.query.get_or_404(course_id)
    
    if request.method == 'POST':
        # Redirect to Stripe Payment Session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': course.title},
                    'unit_amount': int(course.price * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=url_for('payment.success', _external=True),
            cancel_url=url_for('payment.cancel', _external=True),
        )
        return redirect(session.url, code=303)

    return render_template('checkout.html', course=course)

@bp.route('/success')
def success():
    flash('Payment successful!', 'success')
    return redirect(url_for('main.index'))

@bp.route('/cancel')
def cancel():
    flash('Payment canceled.', 'danger')
    return redirect(url_for('main.index'))