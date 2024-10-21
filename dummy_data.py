from datetime import datetime
from app import create_app, db
from app.models import User, Course, Category, Enrollment, Payment, Certificate, Review, Lesson, LessonCompletion, Quiz, Question, QuizAttempt

# Create the Flask application context
app = create_app()

# Use the app context
with app.app_context():
    # Dummy Users
    user1 = User(name='jawad', email='jwd.katten2@gmail.com', role='student')
    user1.set_password('00')
    db.session.add(user1)
    db.session.commit()  # Commit after adding user1

    user2 = User(name='Jane', email='jwd.katten3@gmail.com', role='instructor')
    user2.set_password('00')
    db.session.add(user2)
    db.session.commit()  # Commit after adding user2

    # Dummy Categories
    category1 = Category(name='Programming')
    db.session.add(category1)
    db.session.commit()  # Commit after adding category1

    category2 = Category(name='Data Science')
    db.session.add(category2)
    db.session.commit()  # Commit after adding category2

    # Dummy Courses
    course1 = Course(title='Python for Beginners', description='Learn Python from scratch.', price=29.99, teacher_id=user2.id, category_id=category1.id)
    db.session.add(course1)
    db.session.commit()  # Commit after adding course1

    course2 = Course(title='Data Analysis with Pandas', description='Master data analysis using Pandas.', price=49.99, teacher_id=user2.id, category_id=category2.id)
    db.session.add(course2)
    db.session.commit()  # Commit after adding course2

    # Dummy Lessons
    lesson1 = Lesson(title='Introduction to Python', content='Learn about variables, loops, and conditionals in Python.', course_id=course1.id)
    db.session.add(lesson1)
    db.session.commit()  # Commit after adding lesson1

    lesson2 = Lesson(title='DataFrames in Pandas', content='Learn how to use Pandas DataFrames for data analysis.', course_id=course2.id)
    db.session.add(lesson2)
    db.session.commit()  # Commit after adding lesson2

    # Dummy Enrollments
    enrollment1 = Enrollment(student_id=user1.id, course_id=course1.id)
    db.session.add(enrollment1)
    db.session.commit()  # Commit after adding enrollment1

    enrollment2 = Enrollment(student_id=user1.id, course_id=course2.id)
    db.session.add(enrollment2)
    db.session.commit()  # Commit after adding enrollment2

    # Dummy Payments
    payment1 = Payment(user_id=user1.id, course_id=course1.id, amount=29.99, payment_status='Paid')
    db.session.add(payment1)
    db.session.commit()  # Commit after adding payment1

    payment2 = Payment(user_id=user1.id, course_id=course2.id, amount=49.99, payment_status='Paid')
    db.session.add(payment2)
    db.session.commit()  # Commit after adding payment2

    # Dummy Certificates
    certificate1 = Certificate(student_id=user1.id, course_id=course1.id, certificate_url='https://example.com/cert1')
    db.session.add(certificate1)
    db.session.commit()  # Commit after adding certificate1

    certificate2 = Certificate(student_id=user1.id, course_id=course2.id, certificate_url='https://example.com/cert2')
    db.session.add(certificate2)
    db.session.commit()  # Commit after adding certificate2

    # Dummy Reviews
    review1 = Review(student_id=user1.id, course_id=course1.id, rating=5, comment='Great course, learned a lot!', date_posted=datetime.utcnow())
    db.session.add(review1)
    db.session.commit()  # Commit after adding review1

    review2 = Review(student_id=user1.id, course_id=course2.id, rating=4, comment='Very informative, but a bit fast-paced.', date_posted=datetime.utcnow())
    db.session.add(review2)
    db.session.commit()  # Commit after adding review2

    # Dummy Lesson Completions
    completion1 = LessonCompletion(student_id=user1.id, lesson_id=lesson1.id, completed=True, completion_date=datetime.utcnow())
    db.session.add(completion1)
    db.session.commit()  # Commit after adding completion1

    completion2 = LessonCompletion(student_id=user1.id, lesson_id=lesson2.id, completed=False)
    db.session.add(completion2)
    db.session.commit()  # Commit after adding completion2

    # Dummy Quizzes
    quiz1 = Quiz(title='Python Basics Quiz', course_id=course1.id)
    db.session.add(quiz1)
    db.session.commit()  # Commit after adding quiz1

    quiz2 = Quiz(title='Pandas Quiz', course_id=course2.id)
    db.session.add(quiz2)
    db.session.commit()  # Commit after adding quiz2

    # Dummy Questions
    question1 = Question(question_text='What is a variable?', answer='A storage location for data.', quiz_id=quiz1.id)
    db.session.add(question1)
    db.session.commit()  # Commit after adding question1

    question2 = Question(question_text='What is a DataFrame in Pandas?', answer='A 2-dimensional data structure for data manipulation.', quiz_id=quiz2.id)
    db.session.add(question2)
    db.session.commit()  # Commit after adding question2

    # Dummy Quiz Attempts
    quiz_attempt1 = QuizAttempt(quiz_id=quiz1.id, student_id=user1.id, score=85.0)
    db.session.add(quiz_attempt1)
    db.session.commit()  # Commit after adding quiz_attempt1

    quiz_attempt2 = QuizAttempt(quiz_id=quiz2.id, student_id=user1.id, score=90.0)
    db.session.add(quiz_attempt2)
    db.session.commit()  # Commit after adding quiz_attempt2

    print("Dummy data has been added successfully.")
