import os
import re
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# ✅ Database configuration
db_folder = os.path.join(os.getcwd(), 'database')
if not os.path.exists(db_folder):
    os.makedirs(db_folder)

db_path = os.path.join(db_folder, 'users.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ✅ User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# ✅ Initialize the database
with app.app_context():
    db.create_all()

# ✅ Home route
@app.route('/')
def home():
    return redirect(url_for('dashboard')) if 'user_id' in session else redirect(url_for('login'))

# ✅ Static page (for Netlify/public hosting)
@app.route('/public')
def public_index():
    return send_from_directory('docs', 'index.html')

# ✅ Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Password validation
        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for('signup'))

        if len(password) < 8 or not re.search(r'\d', password) or not re.search(r'[^\w\s]', password):
            flash("Password must be at least 8 characters long, include a number and a special character.", "error")
            return redirect(url_for('signup'))

        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists", "error")
            return redirect(url_for('signup'))

        # Save new user
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')

# ✅ Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash("Login successful", 'success')
            return redirect(url_for('dashboard'))

        flash("Invalid credentials", 'error')
        return redirect(url_for('login'))

    return render_template('login.html')

# ✅ Logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("You have been logged out", 'success')
    return redirect(url_for('login'))

# ✅ Dashboard (protected route)
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please log in first", 'error')
        return redirect(url_for('login'))
    return render_template('dashboard.html')

# ✅ Upload page
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user_id' not in session:
        flash("Please log in first", 'error')
        return redirect(url_for('login'))
    return render_template('upload.html')

# ✅ Profile page
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash("Please log in to view your profile", 'error')
        return redirect(url_for('login'))
    return render_template('profile.html')

# ✅ Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
