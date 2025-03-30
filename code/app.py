from flask import Flask,render_template,redirect, flash,request, url_for, session,flash 
from dotenv import load_dotenv 
from sqlalchemy import func , and_, or_, not_, select
from flask_login import LoginManager, login_user, login_required, current_user, logout_user 
from werkzeug.security import generate_password_hash, check_password_hash 
from sqlalchemy.exc import IntegrityError 
from datetime import datetime
from functools import wraps
import os
from random import shuffle

from models import db, User, Subject, Chapter, Quiz, Questions, Score
from forms import  SubjectForm, RegisterForm , LoginForm , ChapterForm, QuizForm, QuestionForm


load_dotenv()

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

db.init_app(app)

# CREATE LOGIN MANAGER
login_manager = LoginManager()
login_manager.init_app(app)

# CREATE USER LOADER CALLBACK
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, int(user_id))

with app.app_context():
    db.create_all()
    admin = User.query.filter_by(role="ADMIN").first()
    if not admin:
      password = 'adminkey'
      password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
      admin = User(
        name='Admin',
        email='admin@email.com',
        password_hash=password_hash,
        role="ADMIN"
      )
      
      db.session.add(admin)
      db.session.commit()

def admin_required(func):
  @wraps(func)
  def decorated_view(*args, **kwargs):
    if not current_user.is_authenticated or current_user.role != "ADMIN":
      flash("Access denied. Admin role required.", "danger")
      return redirect(url_for('login'))
    return func(*args, **kwargs)
  return decorated_view

@app.context_processor
def inject_global():
  context = {
    'current_user': current_user,
  }
  
  return context

###================================================= HOME =======================================================

@app.route("/")
def home():
    return render_template("home.html")

@app.route('/student/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():  
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            
            # Store user details in session
            session['user_id'] = user.user_id
            session['user_name'] = user.name
            session['user_email'] = user.email

            flash('BOOM!!! Login Successful!', category="success")
            return redirect(url_for('dashboard'))
        else:
            flash("Authentication failed!", category="error")

    return render_template("student_login.html", form=form)



from sqlalchemy.exc import IntegrityError

# User Registration
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered. Please use a different email.', 'danger')
            return redirect(url_for('register'))

        user = User(
            name=form.fullName.data,
            email=form.email.data,
            qualification=form.qualification.data,
            dob=form.dob.data,
            role="STUDENT",
            signup_date=datetime.utcnow(),
        )
        
        user.set_password(form.password.data)

        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()  # Rollback to avoid corruption
            flash('An error occurred during registration. Please try again.', 'danger')

    return render_template("register.html", form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()  # Clear all session data
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))


# User Dashboard
@app.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    if 'user_id' not in session:
        flash("Session expired. Please login again.", "error")
        return redirect(url_for('login'))

    search_query = request.args.get('search', '').strip().lower()
    quizzes = Quiz.query.all()

    if search_query:
        quizzes = [quiz for quiz in quizzes if 
                   search_query in quiz.name.lower() or 
                   search_query in quiz.chapter.name.lower() or 
                   search_query in quiz.chapter.subject.name.lower()]

    scores = Score.query.filter_by(user_id=session['user_id']).all()

    return render_template("student_dashboard.html", quizzes=quizzes, scores=scores, search_query=search_query)



###================================================= ADMIN =======================================================

#Admin Login Page
@app.route('/Admin/login', methods=["GET", "POST"])
def admin_login():
    form = LoginForm()  # Use the existing login form

    if form.validate_on_submit():  # Ensures form is properly submitted
        email = form.email.data
        password = form.password.data

        # Check if admin exists
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()

        if not user or not check_password_hash(user.password_hash, password):
            flash("Incorrect email or password", "danger")
            return redirect(url_for('admin_login'))

        login_user(user)
        flash("Admin login successful!", "success")
        return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard

    return render_template('Admin/admin_login.html', form=form)

#Admin Logout
@app.route('/Admin/logout')
@admin_required
def admin_logout():
  logout_user()
  return redirect(url_for('admin_login'))

#Admin Dashboard
@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if current_user.name != os.getenv('ADMIN_USERNAME'):
         flash("You do not have permission to access this page", category = "error")
         return redirect(url_for('base_login'))
    return render_template("admin/admin_dashboard.html")

@app.route('/admin/summary')
def admin_summary():
    subjects_count = Subject.query.count()
    chapters_count = Chapter.query.count()
    quizzes_count = Quiz.query.count()
    questions_count = Questions.query.count()
    users_count = User.query.filter_by(role="STUDENT").count()
    students = User.query.filter_by(role="STUDENT").all()

    return render_template('admin/summary.html', 
                           subjects_count=subjects_count, 
                           chapters_count=chapters_count, 
                           quizzes_count=quizzes_count, 
                           questions_count=questions_count, 
                           users_count=users_count, 
                           users=students)  # Pass only students to the template

###================================================= SUBJECT =======================================================

@app.route("/admin/manage_subjects")
def manage_subjects():
    if current_user.name != os.getenv('ADMIN_USERNAME'):
        flash("You do not have permission to access this page", category="error")
        return redirect(url_for('home'))
    
    query = request.args.get('query', '').strip()
    
    if query:
        subjects = Subject.query.filter(Subject.name.ilike(f"%{query}%")).all()
    else:
        subjects = Subject.query.all()
    
    return render_template("admin/manage_subjects.html", subject=subjects)

# Add Subject
@app.route("/admin/add_subject", methods=['GET', 'POST'])
@login_required
def add_subject():
    if current_user.name != os.getenv('ADMIN_USERNAME'):
        flash("You don't have permission to access this page", category="error")
        return redirect(url_for("home"))
    form = SubjectForm()
    if form.validate_on_submit():
        subject = Subject(name=form.name.data, description=form.description.data)
        db.session.add(subject)
        db.session.commit()
        flash("Subject added successfully!", category="success")
        return redirect(url_for("manage_subjects"))
    return render_template("admin/add_subjects.html", form=form)

# Edit Subject
@app.route("/admin/edit_subject/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_subject(id):
    if current_user.name != os.getenv('ADMIN_USERNAME'):
        flash("You don't have permission to access this page", category="error")
        return redirect(url_for("home"))
    subject = Subject.query.get_or_404(id)
    form = SubjectForm(obj=subject)
    if form.validate_on_submit():
        subject.name = form.name.data
        subject.description = form.description.data
        db.session.commit()
        flash("Subject updated successfully!", category="success")
        return redirect(url_for("manage_subjects"))
    return render_template("admin/edit_subject.html", form=form)

# Delete Subject
@app.route("/admin/delete_subject/<int:id>")
@login_required
def delete_subject(id):
    if current_user.name != os.getenv('ADMIN_USERNAME'):
        flash("You don't have permission to access this page", category="error")
        return redirect(url_for("home"))
    subject = Subject.query.get_or_404(id)
    db.session.delete(subject)
    db.session.commit()
    flash("Subject deleted successfully!", category="success")
    return redirect(url_for("manage_subjects"))


###================================================= CHAPTER =======================================================

@app.route("/admin/manage_chapters", methods=['GET', 'POST'])
def manage_chapters():
    if current_user.name != os.getenv('ADMIN_USERNAME'):
        flash("You do not have permission to access this page", category="error")
        return redirect(url_for('home'))

    query = request.args.get('query', '').strip()
    
    if query:
        chapters = Chapter.query.filter(Chapter.name.ilike(f"%{query}%")).all()
    else:
        chapters = Chapter.query.all()

    return render_template("admin/manage_chapters.html", chapters=chapters, query=query)

# Add Chapter
@app.route("/admin/add_chapter.html", methods = ['GET', 'POST'])
def add_chapter():
     if current_user.name != os.getenv('ADMIN_USERNAME'):
         flash("You do not have permission to access this page", category = "error")
         return redirect(url_for('home'))
     form = ChapterForm()
     form.subject_id.choices  = [(s.id, s.name) for s in Subject.query.all()]
     if form.validate_on_submit():
          chapter = Chapter(name = form.name.data, description = form.description.data, subject_id = form.subject_id.data )
          db.session.add(chapter)
          db.session.commit()
          flash("Chapter added successfully!", category="success")
          return redirect(url_for("manage_chapters"))
     return render_template("admin/add_chapter.html", form=form)

# Edit Chapter
@app.route("/admin/edit_chapter/<int:id>", methods=['GET', 'POST'])
def edit_chapters(id):
     if current_user.name != os.getenv('ADMIN_USERNAME'):
         flash("You do not have permission to access this page", category = "error")
         return redirect(url_for('home'))
     chapter = Chapter.query.get_or_404(id)
     form = ChapterForm(obj = chapter)
     form.subject_id.choices = [(s.id, s.name) for s in Subject.query.all()]
     if form.validate_on_submit():
          chapter.name = form.name.data
          chapter.description = form.description.data
          db.session.commit()
          flash("Chapter updated successfully!", category="success")
          return redirect(url_for("manage_chapters"))
     return render_template("admin/edit_chapter.html", form=form)

# Delete Chapter
@app.route("/admin/delete_chapter/<int:id>")
@login_required
def delete_chapter(id):
    if current_user.name != os.getenv('ADMIN_USERNAME'):
        flash("You do not have permission to access this page", category="error")
        return redirect(url_for('home'))
    
    chapter = Chapter.query.get_or_404(id)
    db.session.delete(chapter)
    db.session.commit()
    
    flash("Chapter deleted successfully!", category="success")
    return redirect(url_for('manage_chapters'))


###================================================= QUIZZES =======================================================
@app.route("/admin/manage_quizzes", methods=['GET', 'POST'])
def manage_quizzes():
    if current_user.name != os.getenv('ADMIN_USERNAME'):
        flash("You do not have permission to access this page", category="error")
        return redirect(url_for('home'))

    query = request.args.get('query', '').strip()

    if query:
        quizzes = Quiz.query.filter(Quiz.name.ilike(f"%{query}%")).all()
    else:
        quizzes = Quiz.query.all()

    return render_template("admin/manage_quizzes.html", quizzes=quizzes, query=query)

# Add Quiz
@app.route("/admin/add_quiz", methods=['GET', 'POST'])
@login_required
def add_quiz():
    if current_user.name != os.getenv('ADMIN_USERNAME'):
        flash("You don't have permission to access this page", category="error")
        return redirect(url_for("home"))
    form = QuizForm()
    form.chapter_id.choices = [(c.id, c.name) for c in Chapter.query.all()]
    if form.validate_on_submit():
        quiz = Quiz(
            name=form.name.data,
            date_of_quiz=form.date_of_quiz.data,
            time_duration=form.time_duration.data,
            chapter_id=form.chapter_id.data
        )
        db.session.add(quiz)
        db.session.commit()
        flash("Quiz added successfully!", category="success")
        return redirect(url_for("manage_quizzes"))
    return render_template("admin/add_quiz.html", form=form)

# Edit Quiz
@app.route("/admin/edit_quiz/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_quiz(id):
    if current_user.name != os.getenv('ADMIN_USERNAME'):
        flash("You don't have permission to access this page", category="error")
        return redirect(url_for("home"))
    quiz = Quiz.query.get_or_404(id)
    form = QuizForm(obj=quiz)
    form.chapter_id.choices = [(c.id, c.name) for c in Chapter.query.all()]
    if form.validate_on_submit():
        quiz.name = form.name.data
        quiz.date_of_quiz = form.date_of_quiz.data
        quiz.time_duration = form.time_duration.data
        quiz.chapter_id = form.chapter_id.data
        db.session.commit()
        flash("Quiz updated successfully!", category="success")
        return redirect(url_for("manage_quizzes"))
    return render_template("admin/edit_quiz.html", form=form)

# Delete Quiz
@app.route("/admin/delete_quiz/<int:id>", methods=['POST'])
@login_required
def delete_quiz(id):
    if current_user.name != os.getenv('ADMIN_USERNAME'):
        flash("You don't have permission to access this page", category="error")
        return redirect(url_for("home"))
    quiz = Quiz.query.get_or_404(id)
    db.session.delete(quiz)
    db.session.commit()
    flash("Quiz deleted successfully!", category="success")
    return redirect(url_for("manage_quizzes"))

###================================================ QUESTIONS ==============================================
@app.route("/admin/manage_questions/<int:quiz_id>")
@login_required
def manage_quiz_questions(quiz_id):
    if current_user.name != os.getenv('ADMIN_USERNAME'):
        flash("You don't have permission to access this page", category="error")
        return redirect(url_for("home"))

    quiz = Quiz.query.get_or_404(quiz_id)
    query = request.args.get("query", "").strip()

    if query:
        questions = Questions.query.filter(
            Questions.quiz_id == quiz_id,
            Questions.question_statement.ilike(f"%{query}%")
        ).all()
    else:
        questions = quiz.questions

    return render_template("admin/manage_questions.html", quiz=quiz, questions=questions)


# Add Question
@app.route("/admin/add_question/<int:quiz_id>", methods=['GET', 'POST'])
@login_required
def add_question(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if current_user.name != os.getenv('ADMIN_USERNAME'):
        flash("You don't have permission to access this page", category="error")
        return redirect(url_for("home"))
    form = QuestionForm()
    if form.validate_on_submit():
        question = Questions(
            title=form.title.data,
            question_statement=form.question_statement.data,
            option1=form.option1.data,
            option2=form.option2.data,
            option3=form.option3.data,
            option4=form.option4.data,
            correct_option=form.correct_option.data,
            quiz_id=quiz_id
        )
        db.session.add(question)
        db.session.commit()
        flash("Question added successfully!", category="success")
        return redirect(url_for("manage_quiz_questions", quiz_id=quiz_id))
    return render_template("admin/add_question.html", form=form, quiz_name=quiz.name)

# Edit Question
@app.route("/admin/edit_question/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_question(id):
    if current_user.name != os.getenv('ADMIN_USERNAME'):
        flash("You don't have permission to access this page", category="error")
        return redirect(url_for("home"))
    
    question = Questions.query.get_or_404(id)  # Get question by ID
    quiz = Quiz.query.get_or_404(question.quiz_id)  # Get associated quiz
    
    form = QuestionForm(obj=question)

    if form.validate_on_submit():
        question.question_statement = form.question_statement.data
        question.option1 = form.option1.data
        question.option2 = form.option2.data
        question.option3 = form.option3.data
        question.option4 = form.option4.data
        question.correct_option = form.correct_option.data
        db.session.commit()
        flash("Question updated successfully!", category="success")
        return redirect(url_for("manage_quiz_questions", quiz_id=question.quiz_id))

    return render_template("admin/edit_question.html", form=form, quiz_name=quiz.name, question=question)

# Delete Question
@app.route("/admin/delete_question/<int:id>")
@login_required
def delete_question(id):
    if current_user.name != os.getenv('ADMIN_USERNAME'):
        flash("You don't have permission to access this page", category="error")
        return redirect(url_for("home"))
    
    question = Questions.query.get_or_404(id)
    quiz_id = question.quiz_id  # Store quiz ID before deleting for redirection
    db.session.delete(question)
    db.session.commit()
    flash("Question deleted successfully!", category="success")
    return redirect(url_for("manage_quiz_questions", quiz_id=quiz_id))


 
###================================================= MANAGE USERS ===============================================


@app.route("/admin/manage_users")
def manage_users():
     if current_user.name != os.getenv('ADMIN_USERNAME'):
         flash("You do not have permission to access this page", category = "error")
         return redirect(url_for('home'))
     users = User.query.all()
     return render_template("admin/manage_users.html", users = users)


@app.route("/admin/flag_user/<int:user_id>", methods=['POST'])
def flag_user(user_id):
    if current_user.name != os.getenv('ADMIN_USERNAME'):
        flash("You do not have permission to perform this action", category="error")
        return redirect(url_for('manage_users'))

    user = User.query.get(user_id)
    if user:
        user.flagged = not user.flagged
        db.session.commit()
        if user.flagged:
            flash("User has been flagged!", category="warning")
        else:
            flash("User has been unflagged!", category="success")
    else:
        flash("User not found", category="error")

    return redirect(url_for('manage_users'))

@app.route("/admin/delete_user/<int:user_id>", methods=['POST'])
def delete_user(user_id):
    if current_user.name != os.getenv('ADMIN_USERNAME'):
        flash("You do not have permission to perform this action", category="error")
        return redirect(url_for('manage_users'))

    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash("User has been deleted successfully", category="success")
    else:
        flash("User not found", category="error")

    return redirect(url_for('manage_users'))


###================================================= QUIZ =======================================================

from flask import session

@app.route("/quiz/<int:quiz_id>", methods=['GET', 'POST'])
@login_required
def attempt_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    existing_attempt = Score.query.filter_by(user_id=current_user.user_id, quiz_id=quiz_id).first()

    # If reattempting, reset previous attempt
    if existing_attempt:
        db.session.delete(existing_attempt)
        db.session.commit()
        session.pop(f'quiz_{quiz_id}_order', None)  # Clear previous question order

    # Maintain question order across refreshes
    if f'quiz_{quiz_id}_order' in session:
        question_ids = session[f'quiz_{quiz_id}_order']
        questions = sorted(quiz.questions, key=lambda q: question_ids.index(q.id))
    else:
        questions = quiz.questions.copy()
        shuffle(questions)
        session[f'quiz_{quiz_id}_order'] = [q.id for q in questions]  # Save order

    if request.method == 'POST':
        score = 0
        for question in questions:
            user_answer = request.form.get(f'question_{question.id}')
            if user_answer and int(user_answer) == question.correct_option:
                score += 1

        # Save the new attempt
        user_score = Score(total_scored=score, quiz_id=quiz_id, user_id=current_user.user_id)
        db.session.add(user_score)
        db.session.commit()

        # Store quiz attempt in session
        session[f'quiz_{quiz_id}_attempted'] = True
        session.pop(f'quiz_{quiz_id}_order', None)  # Remove order after completion

        flash(f'Quiz completed! Your new score: {score} / {len(questions)}', category="success")
        return redirect(url_for("quiz_results", quiz_id=quiz_id))

    return render_template("attempt_quiz.html", quiz=quiz, questions=questions)

from sqlalchemy import desc
from datetime import datetime, timedelta

@app.route("/quiz_results")
@login_required
def quiz_results():
    # Fetch the latest score per quiz for the current user
    latest_scores = (
        db.session.query(Score)
        .filter(Score.user_id == current_user.user_id)
        .order_by(Score.quiz_id, desc(Score.id))
        .distinct(Score.quiz_id)
        .all()
    )

    if not latest_scores:
        flash("You haven't attempted any quizzes yet.", "info")
        return redirect(url_for("dashboard"))

    quizzes = {score.quiz_id: Quiz.query.get(score.quiz_id) for score in latest_scores}

    # Convert timestamps to IST (UTC+5:30)
    for score in latest_scores:
        if score.timeStamp:
            score.timeStamp = score.timeStamp + timedelta(hours=5, minutes=30)

    # Get search query from request
    search_query = request.args.get('search', '').lower()

    # Filter results based on quiz name, chapter name, or subject name
    if search_query:
        latest_scores = [
            score for score in latest_scores
            if search_query in quizzes[score.quiz_id].name.lower() or
               search_query in quizzes[score.quiz_id].chapter.name.lower() or
               search_query in quizzes[score.quiz_id].chapter.subject.name.lower()
        ]

    return render_template("quiz_results.html", scores=latest_scores, quizzes=quizzes, search_query=search_query)

if __name__ == '__main__':
  app.run(debug=True)