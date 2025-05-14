import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from models.predictor import predict_combined

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# File upload config
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ✅ Prediction Route
@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        flash('No image part', 'error')
        return redirect(url_for('upload'))

    file = request.files['image']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('upload'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        result = predict_combined(filepath)
        return render_template('result.html', prediction=result, image_file=filename)

    flash('Invalid file format', 'error')
    return redirect(url_for('upload'))

# ✅ Database setup
db_folder = os.path.join(os.getcwd(), 'database')
os.makedirs(db_folder, exist_ok=True)
db_path = os.path.join(db_folder, 'users.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ✅ User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

with app.app_context():
    db.create_all()

# ✅ Routes
@app.route('/')
def home():
    return redirect(url_for('dashboard')) if 'user_id' in session else redirect(url_for('login'))

@app.route('/public')
def public_index():
    return send_from_directory('docs', 'index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("Passwords do not match", 'error')
            return redirect(url_for('signup'))

        if User.query.filter_by(username=username).first():
            flash("Username already exists", 'error')
            return redirect(url_for('signup'))

        hashed = generate_password_hash(password, method='pbkdf2:sha256')
        db.session.add(User(username=username, password=hashed))
        db.session.commit()

        flash("Signup successful!", 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            session['user_id'] = user.id
            flash("Login successful", 'success')
            return redirect(url_for('dashboard'))
        flash("Invalid credentials", 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Logged out", 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    return render_template('upload.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

if __name__ == '__main__':
    app.run(debug=True)
