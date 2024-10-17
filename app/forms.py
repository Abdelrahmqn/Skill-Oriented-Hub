# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class QuizForm(FlaskForm):
    submit = SubmitField('Submit Answers')
