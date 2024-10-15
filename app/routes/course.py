import os
import secrets
from PIL import Image
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Course, Enrollment
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, SubmitField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired

bp = Blueprint('course', __name__, url_prefix='/courses')

# Form for creating a course
class CourseForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    courseImage = FileField('Add Image', validators=[FileAllowed(['jpg','png','jfif'])])
    price = FloatField('Price', validators=[DataRequired()])
    submit = SubmitField('Create Course')

# Route display course details
@bp.route('/<int:course_id>')
def course_details(course_id):
    course = Course.query.get_or_404(course_id)
    enrollment = Enrollment.query.filter_by(student_id=current_user.id, course_id=course.id).first()
    enrolled = enrollment is not None

    return render_template('course_details.html', course=course, enrolled=enrolled )

# Function store image
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/img_course', picture_fn)

    # Redimensionner l'image à 125x125 pixels
    output_size = (500, 500)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

# Route for creating a new course (for instructors only)
@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_course():
    if current_user.role != 'instructor':
        flash('Only instructors can create courses.', 'danger')
        return redirect(url_for('main.index'))

    form = CourseForm()
    if form.validate_on_submit():
        if form.courseImage.data:
           course_Image   = save_picture(form.courseImage.data)
        else:
            course_Image  = None

        course = Course(
            title=form.title.data,
            description=form.description.data,
            price=form.price.data,
            teacher_id=current_user.id,
            courseImage= course_Image
        )
        db.session.add(course)
        db.session.commit()
        flash('Course created successfully!', 'success')
        return redirect(url_for('course.instructor_dashboard'))

    return render_template('create_course.html', form=form)

# Route for listing all available courses
@bp.route('/')
def list_courses():
    courses = Course.query.all()
    return render_template('list_courses.html', courses=courses)

# Route for enrolling in a course (for students)
@bp.route('/enroll/<int:course_id>', methods=['POST'])
@login_required
def enroll(course_id):
    if current_user.role != 'student':
        flash('Only students can enroll in courses.', 'danger')
        return redirect(url_for('course.list_courses'))


    course = Course.query.get_or_404(course_id)

    # Check if the student is already enrolled in the course
    enrollment = Enrollment.query.filter_by(student_id=current_user.id, course_id=course.id).first()

    if enrollment:
        flash('You are already enrolled in this course.', 'info')
    else:

        new_enrollment = Enrollment(student_id=current_user.id, course_id=course.id)
        db.session.add(new_enrollment)
        db.session.commit()
        flash('You have successfully enrolled in the course!', 'success')

    return redirect(url_for('course.course_details', course_id=course.id))


# Route for unenrolling from a course (for students)
@bp.route('/unenroll/<int:course_id>', methods=['POST'])
@login_required
def unenroll(course_id):
    # Ensure only students can unenroll
    if current_user.role != 'student':
        flash('Only students can unenroll from courses.', 'danger')
        return redirect(url_for('course.list_courses'))

    course = Course.query.get_or_404(course_id)

    enrollment = Enrollment.query.filter_by(student_id=current_user.id, course_id=course.id).first()

    if enrollment:
        db.session.delete(enrollment)
        db.session.commit()
        flash('You have been successfully unenrolled from the course.', 'success')
    else:
        flash('You are not enrolled in this course.', 'warning')


    return redirect(url_for('course.course_details', course_id=course.id))

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


# Route to delete a course
@bp.route('/delete_course/<int:course_id>', methods=['POST'])
def delete_course(course_id):
    # Find the course by its ID
    course_to_delete = Course.query.get_or_404(course_id)

    # Check if the current user is the instructor (owner of the course)
    if current_user.id == course_to_delete.teacher_id:
        try:
             # delete related enrollments
            Enrollment.query.filter_by(course_id=course_to_delete.id).delete()

             # Delete the course
            db.session.delete(course_to_delete)
            db.session.commit()
            flash('Course has been deleted successfully!', 'success')
        except Exception:
            db.session.rollback()
            flash('There was an issue deleting the course. Please try again.', 'danger')
    else:
        flash('You are not authorized to delete this course.', 'danger')

    return redirect(url_for('course.instructor_dashboard'))
