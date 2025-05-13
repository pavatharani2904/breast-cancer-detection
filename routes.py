import re

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Server-side password checks
        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for('signup'))

        if len(password) < 8 or not re.search(r'\d', password) or not re.search(r'[^\w\s]', password):
            flash("Password must be at least 8 characters long, include a number and a special character.", "error")
            return redirect(url_for('signup'))

        # Save user to database logic
        flash("Account created successfully!", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')
