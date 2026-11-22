from getpass import getpass
from app import create_app
from extensions import db
from models.user import User

app = create_app()

with app.app_context():
    username = input("Username: ").strip()
    email = input("Email: ").strip()
    password = getpass("Password: ")

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        print("Email already exists!")
    else:
        user = User(
            username=username,
            email=email,
            role="admin"
        )

        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        print("Account created successfully!")