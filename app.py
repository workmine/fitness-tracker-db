import sqlite3
import random
from flask import Flask, render_template, g, request, redirect, url_for
# Security import for hashing passwords
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
DATABASE = 'fitness_data.db'

# --- DATABASE FUNCTIONS ---
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

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        
        # 1. Create Dashboard Data Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                steps INTEGER,
                calories INTEGER,
                active_min INTEGER,
                sleep_hours TEXT,
                heart_rate INTEGER,
                weight INTEGER
            )
        ''')

        # 2. Create USERS Table (For Login/Signup)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT UNIQUE,
                password TEXT
            )
        ''')

        # Check if dummy dashboard data exists
        cursor.execute('SELECT count(*) FROM user_stats')
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO user_stats (steps, calories, active_min, sleep_hours, heart_rate, weight)
                VALUES (11500, 780, 65, "7h 30m", 125, 160)
            ''')
            db.commit()

# --- LOGIN & SIGNUP ROUTES ---

@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    
    # Secure the password
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    db = get_db()
    cursor = db.cursor()

    try:
        # Try to insert new user
        cursor.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)', (name, email, hashed_password))
        db.commit()
        # Success! Go to login with success message
        return render_template('login.html', alert_msg="Account created successfully! Please login.")
    except sqlite3.IntegrityError:
        # Error: Email already exists
        return render_template('signup.html', error_msg="Email already registered. Try logging in.")

@app.route('/login', methods=['POST'])
def handle_login():
    email = request.form['email']
    password = request.form['password']

    db = get_db()
    cursor = db.cursor()
    
    # Find user by email
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()

    if user and check_password_hash(user['password'], password):
        # Password Match! Go to Menu
        return redirect(url_for('main_menu'))
    else:
        # Wrong details
        return render_template('login.html', error_msg="Invalid email or password.")

# --- FORGOT PASSWORD ROUTES ---
@app.route('/forgot_password')
def forgot_password_page():
    return render_template('forgot_password.html')

@app.route('/perform_reset', methods=['POST'])
def perform_reset():
    email = request.form['email']
    print(f"--- RESET LINK SENT TO: {email} ---")
    return render_template('login.html', alert_msg="Reset link sent! Please check your email.")

# --- APP MENU & DASHBOARDS ---

@app.route('/menu')
def main_menu():
    return render_template('index.html')

@app.route('/dashboard1')
def dashboard1():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM user_stats ORDER BY id DESC LIMIT 1')
    data = cursor.fetchone()
    return render_template('dashboard1.html', steps=data['steps'], cals=data['calories'], active=data['active_min'], sleep=data['sleep_hours'])

@app.route('/dashboard2')
def dashboard2():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM user_stats ORDER BY id DESC LIMIT 1')
    data = cursor.fetchone()
    return render_template('dashboard2.html', steps=data['steps'], cals=data['calories'], bpm=data['heart_rate'], sleep=data['sleep_hours'])

@app.route('/dashboard3')
def dashboard3():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM user_stats ORDER BY id DESC LIMIT 1')
    data = cursor.fetchone()
    return render_template('dashboard3.html', steps=data['steps'], cals=data['calories'], sleep=data['sleep_hours'])

@app.route('/dashboard4')
def dashboard4():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM user_stats ORDER BY id DESC LIMIT 1')
    data = cursor.fetchone()
    return render_template('dashboard4.html', steps=data['steps'], cals=data['calories'], active=data['active_min'], sleep=data['sleep_hours'], hr=data['heart_rate'], weight=data['weight'])

@app.route('/simulate_update')
def simulate_update():
    db = get_db()
    cursor = db.cursor()
    new_steps = random.randint(5000, 15000)
    new_cals = random.randint(400, 1200)
    new_active = random.randint(30, 120)
    new_hr = random.randint(60, 140)
    cursor.execute('UPDATE user_stats SET steps=?, calories=?, active_min=?, heart_rate=? WHERE id=1', (new_steps, new_cals, new_active, new_hr))
    db.commit()
    return "Data Updated!"

if __name__ == '__main__':
    init_db()
    app.run(debug=True)