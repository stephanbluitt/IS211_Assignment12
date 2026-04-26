from flask import Flask, render_template, request, redirect, url_for, session, flash, g
import sqlite3
from functools import wraps

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_is211'
DATABASE = 'hw13.db'

# --- Database Helper Functions ---
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# --- Authentication Decorator ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash("Please log in to access this page.", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Routes ---
@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'password':
            session['logged_in'] = True
            flash("You were successfully logged in.", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials. Please try again.", "error")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    students = db.execute('SELECT * FROM students').fetchall()
    quizzes = db.execute('SELECT * FROM quizzes').fetchall()
    return render_template('dashboard.html', students=students, quizzes=quizzes)

@app.route('/student/add', methods=['GET', 'POST'])
@login_required
def add_student():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        if not first_name or not last_name:
            flash("First and Last name are required.", "error")
        else:
            db = get_db()
            db.execute('INSERT INTO students (first_name, last_name) VALUES (?, ?)', (first_name, last_name))
            db.commit()
            flash("Student added successfully.", "success")
            return redirect(url_for('dashboard'))
    return render_template('add_student.html')

@app.route('/quiz/add', methods=['GET', 'POST'])
@login_required
def add_quiz():
    if request.method == 'POST':
        subject = request.form['subject']
        num_questions = request.form['num_questions']
        quiz_date = request.form['quiz_date']
        if not subject or not num_questions or not quiz_date:
            flash("All fields are required.", "error")
        else:
            db = get_db()
            db.execute('INSERT INTO quizzes (subject, num_questions, quiz_date) VALUES (?, ?, ?)', 
                       (subject, num_questions, quiz_date))
            db.commit()
            flash("Quiz added successfully.", "success")
            return redirect(url_for('dashboard'))
    return render_template('add_quiz.html')

@app.route('/student/<int:id>')
@login_required
def view_results(id):
    db = get_db()
    student = db.execute('SELECT * FROM students WHERE id = ?', (id,)).fetchone()
    # Optional Part: Using JOIN to expand results output
    query = '''
        SELECT q.id, q.subject, q.quiz_date, r.score 
        FROM results r 
        JOIN quizzes q ON r.quiz_id = q.id 
        WHERE r.student_id = ?
    '''
    results = db.execute(query, (id,)).fetchall()
    return render_template('student_results.html', student=student, results=results)

@app.route('/results/add', methods=['GET', 'POST'])
@login_required
def add_result():
    db = get_db()
    if request.method == 'POST':
        student_id = request.form['student_id']
        quiz_id = request.form['quiz_id']
        score = request.form['score']
        if not student_id or not quiz_id or not score:
            flash("All fields are required.", "error")
        else:
            db.execute('INSERT INTO results (student_id, quiz_id, score) VALUES (?, ?, ?)', 
                       (student_id, quiz_id, score))
            db.commit()
            flash("Result added successfully.", "success")
            return redirect(url_for('dashboard'))
            
    students = db.execute('SELECT * FROM students').fetchall()
    quizzes = db.execute('SELECT * FROM quizzes').fetchall()
    return render_template('add_result.html', students=students, quizzes=quizzes)

if __name__ == '__main__':
    app.run(debug=True)
