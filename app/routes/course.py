from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Course, Enrollment
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, SubmitField
from wtforms.validators import DataRequired

bp = Blueprint('course', __name__, url_prefix='/courses')

# Form for creating a course
class CourseForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    submit = SubmitField('Create Course')

@bp.route('/<int:course_id>')
def course_details(course_id):
    course = Course.query.get_or_404(course_id)
    return render_template('course_details.html', course=course)

# Route for creating a new course (for instructors only)
@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_course():
    # if current_user.role != 'instructor':
    #     flash('Only instructors can create courses.', 'danger')
    #     return redirect(url_for('main.index'))
    print(f"Current user role: {current_user.role}")
    form = CourseForm()
    if form.validate_on_submit():
        try:
            # Debug output for form values
            print(f"Creating Course: {form.title.data}, Price: {form.price.data}")

            course = Course(
                title=form.title.data,
                description=form.description.data,
                price=form.price.data,
                teacher_id=current_user.id
            )
            db.session.add(course)
            db.session.commit()

            flash('Course created successfully!', 'success')
            return redirect(url_for('course.list_courses'))
        except Exception as e:
            # bugs
            print(f"Error: {str(e)}")
            db.session.rollback()
            flash('An error occurred while creating the course.', 'danger')

    return render_template('create_course.html', form=form)

# Route for listing all available courses
@bp.route('/')
def list_courses():
    courses = Course.query.all()
    return render_template('list_courses.html', courses=courses)

# Route for enrolling in a course (for students)
@bp.route('/enroll/<int:course_id>')
@login_required
def enroll(course_id):
    if current_user.role != 'student':
        flash('Only students can enroll in courses.', 'danger')
        return redirect(url_for('course.list_courses'))

    course = Course.query.get_or_404(course_id)
    enrollment = Enrollment.query.filter_by(student_id=current_user.id, course_id=course.id).first()

    if enrollment:
        flash('You are already enrolled in this course.', 'info')
    else:
        new_enrollment = Enrollment(student_id=current_user.id, course_id=course.id)
        db.session.add(new_enrollment)
        db.session.commit()
        flash('You have successfully enrolled in the course!', 'success')

    return redirect(url_for('course.list_courses'))
@bp.route('/instructor/dashboard')
@login_required
def instructor_dashboard():
    if current_user.role != 'instructor':
        flash('Only instructors can access the dashboard.', 'danger')
        return redirect(url_for('main.index'))

    courses = Course.query.filter_by(teacher_id=current_user.id).all()
    return render_template('instructor_dashboard.html', courses=courses)
@bp.route('/student/dashboard')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        flash('Only students can access the dashboard.', 'danger')
        return redirect(url_for('main.index'))

    enrollments = Enrollment.query.filter_by(student_id=current_user.id).all()
    return render_template('student_dashboard.html', enrollments=enrollments)
@bp.route('/edit/<int:course_id>', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    if current_user.role != 'instructor':
        flash('Only instructors can edit courses.', 'danger')
        return redirect(url_for('main.index'))

    course = Course.query.get_or_404(course_id)
    if course.teacher_id != current_user.id:
        flash('You do not have permission to edit this course.', 'danger')
        return redirect(url_for('course.instructor_dashboard'))

    form = CourseForm(obj=course)
    if form.validate_on_submit():
        course.title = form.title.data
        course.description = form.description.data
        course.price = form.price.data
        db.session.commit()
        flash('Course updated successfully!', 'success')
        return redirect(url_for('course.instructor_dashboard'))

    return render_template('edit_course.html', form=form, course=course)
