import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from models.predictor import predict_combined
from flask import jsonify

app = Flask(__name__)
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.getcwd(), 'database', 'users.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

with app.app_context():
    os.makedirs('database', exist_ok=True)
    db.create_all()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return redirect(url_for('dashboard')) if 'user_id' in session else redirect(url_for('login'))

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
        
        db.session.add(User(username=username, password=password))

        db.session.commit()
        flash("Signup successful! Please log in.", 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(f"Trying login for username: {username}")  # debug print

        user = User.query.filter_by(username=username).first()
        if user:
            print(f"User found: {user.username}")
            if user.password == password:
                print("Password match!")
                session['user_id'] = user.id
                flash("Login successful", 'success')
                return redirect(url_for('dashboard'))
            else:
                print("Password mismatch!")
        else:
            print("User not found!")

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
@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    return render_template('upload.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        flash('No image part', 'error')
        return redirect(url_for('upload'))

    file = request.files['image']
    if file.filename == '' or not allowed_file(file.filename):
        flash('Invalid file', 'error')
        return redirect(url_for('upload'))

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    prediction = predict_combined(filepath)
    return render_template('results.html', prediction=prediction, image_path=filepath)

@app.route('/retrain', methods=['POST'])
def retrain():
    from models.train import retrain_model  # Import your retraining logic
    accuracy = retrain_model()
    return jsonify({"message": "Retraining complete", "validation_accuracy": accuracy})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
