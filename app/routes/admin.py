from flask import Blueprint, render_template, redirect, url_for, flash
from sqlalchemy import func
from app.models import User, Course, Category, Enrollment
from flask_login import login_required, current_user
from app import db
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email
from wtforms.fields.choices import RadioField

bp = Blueprint('admin', __name__)

@bp.route('/admin')
@login_required
def admin():
    if current_user.role != "admin":
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('main.index'))

    # User Statistics
    nb_students = User.query.filter_by(role='student').count()
    nb_instructors = User.query.filter_by(role='instructor').count()

    # Course Statistics
    popular_courses = (
    db.session.query(Course, func.count(Enrollment.id).label('enrollment_count'))
    .join(Enrollment, Enrollment.course_id == Course.id)
    .group_by(Course.id)
    .order_by(func.count(Enrollment.id).desc())
    .limit(5)
    .all()
)


    # # Financial Statistics
    # total_revenue = Payment.query.with_entities(db.func.sum(Payment.amount)).scalar() or 0
    # pending_payments = Payment.query.filter_by(status='pending').count()

    # Category Management
    categories = Category.query.all()

    return render_template(
        'admin/admin_dashboard.html',
        nb_students=nb_students,
        nb_instructors=nb_instructors,
        popular_courses=popular_courses,
        categories=categories
    )

@bp.route('/admin/manage-users')
@login_required
def manage_users():
    if current_user.role != "admin":
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))

    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)


class EditUserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update')


# Edit user route
@bp.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = EditUserForm()

    if form.validate_on_submit():
        user.name = form.name.data
        user.email = form.email.data
        db.session.commit()

        flash(f'User {user.name} updated successfully!', 'success')
        return redirect(url_for('admin.manage_users'))

    form.name.data = user.name
    form.email.data = user.email

    return render_template('admin/edit_user.html', user=user, form=form)


# # Disable user route
# @bp.route('/admin/disable_user/<int:user_id>', methods=['POST'])
# def disable_user(user_id):
#     user = User.query.get_or_404(user_id)
#     user.active = False
#     db.session.commit()
#     flash(f'User {user.name} has been disabled.', 'warning')
#     return redirect(url_for('admin.manage_users'))

# # Enable user route
# @bp.route('/admin/enable_user/<int:user_id>', methods=['POST'])
# def enable_user(user_id):
#     user = User.query.get_or_404(user_id)
#     user.active = True
#     db.session.commit()
#     flash(f'User {user.name} has been enabled.', 'success')
#     return redirect(url_for('admin.manage_users'))

# Delete user route

# Delete user route
# Delete user route
@bp.route('/admin/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    # Check if the user has enrollments
    enrollments = Enrollment.query.filter_by(student_id=user_id).all()

    if enrollments:
        # If user is enrolled in courses, unenroll them first
        for enrollment in enrollments:
            db.session.delete(enrollment)
        db.session.commit()
        flash(f'User {user.name} has been unenrolled from {len(enrollments)} courses.', 'warning')

    # Proceed with the deletion of the user
    db.session.delete(user)
    db.session.commit()

    flash(f'User {user.name} has been deleted.', 'danger')
    return redirect(url_for('admin.manage_users'))

class AddUserForm(FlaskForm):

    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = RadioField('Role', choices=[('student', 'Student'), ('instructor', 'Instructor'), ('admin','Admin')], validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Add User')


# Route to add a new user
@bp.route('/admin/add_user', methods=['GET', 'POST'])
def add_user():
    form = AddUserForm()  # Assuming you have a form class AddUserForm

    if form.validate_on_submit():
        # Create a new User object
        user = User(
            name=form.name.data,
            email=form.email.data,
            role=form.role.data,
        )
        user.set_password(form.password.data)  # Hash the password

        db.session.add(user)
        db.session.commit()

        flash(f'User {user.name} has been added successfully!', 'success')
        return redirect(url_for('admin.manage_users'))

    return render_template('admin/add_user.html', form=form)
