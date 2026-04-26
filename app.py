from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'secret'

def get_db():
    return sqlite3.connect('hw13.db')

# ------------------------
# LOGIN
# ------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'password':
            session['logged_in'] = True
            return redirect('/dashboard')
        else:
            error = 'Invalid credentials'
    return render_template('login.html', error=error)

def check_login():
    if not session.get('logged_in'):
        return False
    return True

# ------------------------
# DASHBOARD
# ------------------------
@app.route('/dashboard')
def dashboard():
    if not check_login():
        return redirect('/login')

    db = get_db()
    students = db.execute("SELECT * FROM students").fetchall()
    quizzes = db.execute("SELECT * FROM quizzes").fetchall()

    return render_template('dashboard.html', students=students, quizzes=quizzes)

# ------------------------
# ADD STUDENT
# ------------------------
@app.route('/student/add', methods=['GET', 'POST'])
def add_student():
    if not check_login():
        return redirect('/login')

    if request.method == 'POST':
        db = get_db()
        db.execute(
            "INSERT INTO students (first_name, last_name) VALUES (?, ?)",
            (request.form['first_name'], request.form['last_name'])
        )
        db.commit()
        return redirect('/dashboard')

    return render_template('add_student.html')

# ------------------------
# ADD QUIZ
# ------------------------
@app.route('/quiz/add', methods=['GET', 'POST'])
def add_quiz():
    if not check_login():
        return redirect('/login')

    if request.method == 'POST':
        db = get_db()
        db.execute(
            "INSERT INTO quizzes (subject, num_questions, quiz_date) VALUES (?, ?, ?)",
            (request.form['subject'], request.form['num_questions'], request.form['quiz_date'])
        )
        db.commit()
        return redirect('/dashboard')

    return render_template('add_quiz.html')

# ------------------------
# STUDENT RESULTS
# ------------------------
@app.route('/student/<int:id>')
def student_results(id):
    if not check_login():
        return redirect('/login')

    db = get_db()
    results = db.execute(
        "SELECT quiz_id, score FROM results WHERE student_id = ?",
        (id,)
    ).fetchall()

    return render_template('student_results.html', results=results)

# ------------------------
# ADD RESULT
# ------------------------
@app.route('/results/add', methods=['GET', 'POST'])
def add_result():
    if not check_login():
        return redirect('/login')

    db = get_db()

    if request.method == 'POST':
        db.execute(
            "INSERT INTO results (student_id, quiz_id, score) VALUES (?, ?, ?)",
            (request.form['student_id'], request.form['quiz_id'], request.form['score'])
        )
        db.commit()
        return redirect('/dashboard')

    students = db.execute("SELECT * FROM students").fetchall()
    quizzes = db.execute("SELECT * FROM quizzes").fetchall()

    return render_template('add_result.html', students=students, quizzes=quizzes)

# ------------------------
if __name__ == '__main__':
    app.run(debug=True)
