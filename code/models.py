from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()

class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    password_hash = db.Column(db.String(64), nullable=False)
    qualification = db.Column(db.String(80), nullable=True)
    dob = db.Column(db.Date)
    role = db.Column(db.String(24), nullable=False)
    image = db.Column(db.String(255), default='profile.png')
    signup_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    flagged = db.Column(db.Boolean, nullable=False, default=False)


    scores = db.relationship('Score', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def get_id(self):
        return str(self.user_id)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"User('{self.username}', '{self.fullName}')"

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    chapters = db.relationship('Chapter', backref='subject', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f"Subject('{self.name}')"

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id', ondelete='CASCADE'), nullable=False)

    quizzes = db.relationship('Quiz', backref='chapter', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f"Chapter('{self.name}')"

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_of_quiz = db.Column(db.DateTime)
    time_duration = db.Column(db.Integer, nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id', ondelete='CASCADE'), nullable=False)

    questions = db.relationship('Questions', backref='quiz', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f"Quiz('{self.name}', '{self.date_of_quiz}')"

class Questions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    question_statement = db.Column(db.Text)
    option1 = db.Column(db.String(200), nullable=False)
    option2 = db.Column(db.String(200), nullable=False)
    option3 = db.Column(db.String(200), nullable=False)
    option4 = db.Column(db.String(200), nullable=False)
    correct_option = db.Column(db.Integer, nullable=False)

    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id', ondelete='CASCADE'), nullable=False)

    def __repr__(self):
        return f"Question('{self.title}')"

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total_scored = db.Column(db.Integer, nullable=False)
    timeStamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False)

    def __repr__(self):
        return f"Score('{self.total_scored}', '{self.timeStamp}')"
