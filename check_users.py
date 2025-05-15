from app import app, db, User  # Import your app instance too!

with app.app_context():
    users = User.query.all()
    if not users:
        print("No users found in the database!")
    else:
        for user in users:
            print(f"Username: {user.username}, Password Hash: {user.password}")
