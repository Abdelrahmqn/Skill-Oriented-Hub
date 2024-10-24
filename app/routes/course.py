import logging
import os
import secrets
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from wtforms import StringField, TextAreaField, FloatField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed
from PIL import Image


from app import db
from app.models import Course, Enrollment, Category, Lesson, Question, Quiz, QuizAttempt, Payment
from app.utils import delete_file_if_exists, save_file, get_embed_url

logging.basicConfig(level=logging.DEBUG)


bp = Blueprint('course', __name__, url_prefix='/courses')

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired()])
    submit = SubmitField('Add Category')

@bp.route('/add_category', methods=['GET', 'POST'])
@login_required
def add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category_name = form.name.data
        existing_category = Category.query.filter_by(name=category_name).first()

        if existing_category:
            flash('Category already exists!', 'danger')
        else:
            new_category = Category(name=category_name)
            db.session.add(new_category)
            db.session.commit()
            flash('Category added successfully!', 'success')
            return redirect(url_for('course.create_course'))  # Redirect to wherever appropriate in your app

    return render_template('admin/add_category.html', form=form)





# Form for creating a course
class CourseForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    courseImage = FileField('Add Image', validators=[FileAllowed(['jpg','png','jfif'])])
    price = FloatField('Price', validators=[DataRequired()])
    category_id = SelectField('Category', validators=[DataRequired()], coerce=int)
    submit = SubmitField('Create Course')

    def __init__(self, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)
        self.category_id.choices = [(category.id, category.name) for category in Category.query.all()]

# Route display course details
@bp.route('/<int:course_id>')
def course_details(course_id):
    course = Course.query.get_or_404(course_id)
    enrollment = Enrollment.query.filter_by(student_id=current_user.id, course_id=course.id).first()
    enrolled = enrollment is not None

    return render_template('course/course_details.html', course=course, enrolled=enrolled )


# Route to display all lessons in the course
@bp.route('/progress/<int:course_id>')
@login_required
def course_progress(course_id):
    # Fetch the course or return 404 if not found
    course = Course.query.get_or_404(course_id)

    # Ensure the student is enrolled in the course
    enrollment = Enrollment.query.filter_by(student_id=current_user.id, course_id=course.id).first()
    enrolled = enrollment is not None

    # If the user is not enrolled, redirect to the course details page
    if current_user.role == 'student' and not enrolled:
        flash('You must be enrolled in the course to view the lessons.', 'danger')
        return redirect(url_for('course.course_details', course_id=course.id))

    # Fetch all lessons related to the course
    lessons = Lesson.query.filter_by(course_id=course.id).all()

    # Render the template to show the course and its lessons
    return render_template('course/course_progress.html', course=course, lessons=lessons, enrolled=enrolled, get_embed_url=get_embed_url)




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

        selected_category = Category.query.get(form.category_id.data)

        course = Course(
            title=form.title.data,
            description=form.description.data,
            price=form.price.data,
            teacher_id=current_user.id,
            courseImage= course_Image,
            category_id=selected_category.id
        )
        db.session.add(course)
        db.session.commit()
        flash('Course created successfully!', 'success')
        return redirect(url_for('course.instructor_dashboard'))

    return render_template('course/create_course.html', form=form)


# Route for listing all available courses
@bp.route('/')
def list_courses():
    courses = Course.query.all()
    categories = Category.query.all()

    return render_template('course/list_courses.html', courses=courses, categories=categories)


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
        flash('You have been successfully unenrolled from the course.', 'success')

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
    return render_template('dashboard/instructor_dashboard.html', courses=courses)


@bp.route('/student/dashboard')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        flash('Only students can access the dashboard.', 'danger')
        return redirect(url_for('main.index'))



    enrollments = Enrollment.query.filter_by(student_id=current_user.id).all()
    return render_template('dashboard/student_dashboard.html', enrollments=enrollments)


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
        course.category_id = form.category_id.data
        db.session.commit()

        flash('Course updated successfully!', 'success')
        return redirect(url_for('course.instructor_dashboard'))

    return render_template('course/edit_course.html', form=form, course=course)


@bp.route('/<int:course_id>/lessons', methods=['GET', 'POST'])
@login_required
def add_lesson(course_id):
    if current_user.role != 'instructor':
        flash('Only instructors can add lessons.', 'danger')
        return redirect(url_for('main.index'))

    course = Course.query.get_or_404(course_id)
    if course.teacher_id != current_user.id:
        flash('You do not have permission to add lessons to this course.', 'danger')
        return redirect(url_for('course.instructor_dashboard'))

    form = LessonForm()
    if form.validate_on_submit():
        video_path = None

        # Save the video file if uploaded
        if form.video_file.data:
            video_filename = secure_filename(form.video_file.data.filename)
            video_path = f'uploads/{video_filename}'
            form.video_file.data.save(f'uploads/{video_filename}')

        lesson = Lesson(
            title=form.title.data,
            content=form.content.data,
            youtube_link=form.youtube_link.data,
            video_path=video_path,
            course_id=course.id
        )
        db.session.add(lesson)
        db.session.commit()
        flash('Lesson added successfully!', 'success')
        return redirect(url_for('course.course_details', course_id=course.id))

    return render_template('course/add_lesson.html', form=form, course=course)


# Form for adding a lesson
class LessonForm(FlaskForm):
    title = StringField('Lesson Title', validators=[DataRequired()])
    content = TextAreaField('Lesson Content', validators=[DataRequired()])
    youtube_link = StringField('YouTube Link')  # New YouTube Link field
    video_file = FileField('Upload Video', validators=[FileAllowed(['mp4', 'mov', 'avi'], 'Video files only!')])  # New File upload field
    submit = SubmitField('Add/Update Lesson')


@bp.route('/<int:course_id>/quizzes', methods=['GET', 'POST'])
@login_required
def add_quiz(course_id):
    if current_user.role != 'instructor':
        flash('Only instructors can add quizzes.', 'danger')
        return redirect(url_for('main.index'))

    course = Course.query.get_or_404(course_id)
    if course.teacher_id != current_user.id:
        flash('You do not have permission to add quizzes to this course.', 'danger')
        return redirect(url_for('course.instructor_dashboard'))

    form = QuizForm()
    if form.validate_on_submit():
        quiz = Quiz(title=form.title.data, course_id=course.id)
        db.session.add(quiz)
        db.session.commit()
        flash('Quiz added successfully!', 'success')
        return redirect(url_for('course.course_details', course_id=course.id))

    return render_template('course/add_quiz.html', form=form, course=course)


@bp.route('/<int:quiz_id>/questions', methods=['GET', 'POST'])
@login_required
def add_question(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    course = quiz.course

    if current_user.role != 'instructor' or course.teacher_id != current_user.id:
        flash('Only instructors can add questions.', 'danger')
        return redirect(url_for('main.index'))

    form = QuestionForm()
    if form.validate_on_submit():
        question = Question(question_text=form.question_text.data, answer=form.answer.data, quiz_id=quiz.id)
        db.session.add(question)
        db.session.commit()
        flash('Question added successfully!', 'success')
        return redirect(url_for('course.course_details', course_id=course.id))

    return render_template('course/add_question.html', form=form, quiz=quiz)


# Forms for quizzes and questions
class QuizForm(FlaskForm):
    title = StringField('Quiz Title', validators=[DataRequired()])
    submit = SubmitField('Add Quiz')


class QuestionForm(FlaskForm):
    question_text = TextAreaField('Question', validators=[DataRequired()])
    answer = StringField('Answer', validators=[DataRequired()])
    submit = SubmitField('Add Question')


@bp.route('/lesson/<int:lesson_id>', methods=['GET'])
@login_required
def view_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    course = lesson.course

    # Ensure student is enrolled in the course
    if current_user.role == 'student' and current_user.id not in [enrollment.student_id for enrollment in course.enrollments]:
        flash('You must be enrolled in the course to view this lesson.', 'danger')
        return redirect(url_for('course.course_details', course_id=course.id))

    # Convert YouTube link to embed format if necessary
    if lesson.youtube_link:
        lesson.youtube_link = get_embed_url(lesson.youtube_link)

    return render_template('course/view_lesson.html', lesson=lesson)

@bp.route('/quiz/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    course = quiz.course

    # Ensure student is enrolled in the course
    if current_user.role == 'student' and current_user.id not in [enrollment.student_id for enrollment in course.enrollments]:
        flash('You must be enrolled in the course to take this quiz.', 'danger')
        return redirect(url_for('course.course_details', course_id=course.id))

    # Check if the student has already attempted this quiz
    if current_user.role == 'student':
        existing_attempt = QuizAttempt.query.filter_by(quiz_id=quiz.id, student_id=current_user.id).first()
        if existing_attempt:
            flash(f'You have already completed this quiz and scored {existing_attempt.score}%.', 'info')
            return redirect(url_for('course.course_details', course_id=course.id))

    # Create a dynamic form class
    class DynamicQuizForm(FlaskForm):
        submit = SubmitField('Submit Answers')

    # Instantiate the form and dynamically add fields
    form = DynamicQuizForm()

    for question in quiz.questions:
        field_name = f'question_{question.id}'
        field = StringField(question.question_text, validators=[DataRequired()])
        setattr(DynamicQuizForm, field_name, field)

    form = DynamicQuizForm()  # Re-instantiate form after adding new fields

    # Handle form submission
    if form.validate_on_submit():
        logging.info("Form submitted successfully")

        # Evaluate the quiz answers
        correct_answers = 0
        total_questions = len(quiz.questions)
        results = []

        for question in quiz.questions:
            student_answer = form.data.get(f'question_{question.id}')
            correct = False
            if student_answer and student_answer.strip().lower() == question.answer.strip().lower():
                correct_answers += 1
                correct = True
            results.append({
                'question': question.question_text,
                'your_answer': student_answer,
                'correct_answer': question.answer,
                'is_correct': correct
            })

        # Calculate the score
        score = (correct_answers / total_questions) * 100

        # Record the quiz attempt in the database
        quiz_attempt = QuizAttempt(
            quiz_id=quiz.id,
            student_id=current_user.id,
            score=score
        )
        db.session.add(quiz_attempt)
        db.session.commit()

        # Show feedback to the student
        return render_template(
            'course/quiz_results.html',
            quiz=quiz,
            results=results,
            correct_answers=correct_answers,
            total_questions=total_questions,
            score=score
        )
    else:
        logging.info("Form validation failed")
        logging.info(f"Form data: {form.data}")
        logging.info(f"Form validation errors: {form.errors}")

    # Render the quiz form for students
    return render_template('course/take_quiz.html', quiz=quiz, form=form)

@bp.route('/quiz/<int:quiz_id>/questions', methods=['GET', 'POST'])
@login_required
def view_questions(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    course = quiz.course

    if current_user.role != 'instructor' or course.teacher_id != current_user.id:
        flash('Only instructors can view and edit questions.', 'danger')
        return redirect(url_for('main.index'))

    form = QuestionForm()
    if form.validate_on_submit():
        # Add or update questions here
        question = Question(question_text=form.question_text.data, answer=form.answer.data, quiz_id=quiz.id)
        db.session.add(question)
        db.session.commit()
        flash('Question added successfully!', 'success')
        return redirect(url_for('course.view_questions', quiz_id=quiz.id))

    questions = Question.query.filter_by(quiz_id=quiz.id).all()
    return render_template('course/view_questions.html', form=form, quiz=quiz, questions=questions)


@bp.route('/question/<int:question_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)
    quiz = question.quiz
    course = quiz.course

    if current_user.role != 'instructor' or course.teacher_id != current_user.id:
        flash('Only instructors can edit questions.', 'danger')
        return redirect(url_for('main.index'))

    form = QuestionForm(obj=question)
    if form.validate_on_submit():
        question.question_text = form.question_text.data
        question.answer = form.answer.data
        db.session.commit()
        flash('Question updated successfully!', 'success')
        return redirect(url_for('course.view_questions', quiz_id=quiz.id))

    return render_template('course/edit_question.html', form=form, question=question)



@bp.route('/lesson/<int:lesson_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_lesson(lesson_id):
    # Get the lesson object
    lesson = Lesson.query.get_or_404(lesson_id)
    course = lesson.course

    # Verify if the current user is the instructor of the course
    if current_user.role != 'instructor' or course.teacher_id != current_user.id:
        flash('You do not have permission to edit this lesson.', 'danger')
        return redirect(url_for('course.course_details', course_id=course.id))

    # Create the form and populate it with the current lesson details
    form = LessonForm(obj=lesson)

    if form.validate_on_submit():
        # Update the lesson fields
        lesson.title = form.title.data
        lesson.content = form.content.data
        lesson.youtube_link = form.youtube_link.data

        # Handle video file upload
        if form.video_file.data:
            # Remove existing video if there is a new upload
            if lesson.video_path:
                delete_file_if_exists(lesson.video_path)  # Helper function to delete old files

            # Save the new video file
            video_filename = save_file(form.video_file.data)  # Helper function to save the file
            lesson.video_path = video_filename

        # Save changes to the database
        db.session.commit()
        flash('Lesson updated successfully!', 'success')
        return redirect(url_for('course.course_details', course_id=course.id))

    return render_template('course/edit_lesson.html', form=form, course=course, lesson=lesson)
