from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, SubmitField, TextAreaField, SelectField, DateTimeLocalField,IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=8), DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[EqualTo('password'), DataRequired()])
    fullName = StringField('Full Name', validators=[DataRequired()])
    qualification = StringField('Qualification', validators=[DataRequired()])
    dob = DateField('Date of Birth', format="%Y-%m-%d", validators=[DataRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Email(), DataRequired()])
    password = PasswordField('Password', validators=[Length(min=8), DataRequired()])
    submit = SubmitField('Login')


class SubjectForm(FlaskForm):
    name = StringField('Name', validators = [DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Save')


class ChapterForm(FlaskForm):
    name = StringField('Name' , validators=[DataRequired()])
    description = TextAreaField('Description')
    subject_id = SelectField('Subject' , coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save')

class QuizForm(FlaskForm):
    name = StringField('Name' , validators=[DataRequired()])
    date_of_quiz = DateTimeLocalField('Date of Quiz', validators=[DataRequired()])
    time_duration = IntegerField('Duration')
    chapter_id = SelectField('Chapter' , coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save') 


class QuestionForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    question_statement = TextAreaField('Question Statement', validators=[DataRequired()])
    option1 = StringField('Option 1', validators=[DataRequired()])
    option2 = StringField('Option 2', validators=[DataRequired()])
    option3 = StringField('Option 3', validators=[DataRequired()])
    option4 = StringField('Option 4', validators=[DataRequired()])
    correct_option = IntegerField('Correct Option (1-4)', validators=[DataRequired()])
    submit = SubmitField('Save')
