from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def login():
    return render_template('index.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/result')
def result():
    return render_template('result.html', prediction='malignant', confidence=93.5)

if __name__ == '__main__':
    app.run(debug=True)
