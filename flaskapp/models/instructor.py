from flaskapp import db, login
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

class Instructor(UserMixin, db.Model):
    __tablename__ = "instructors"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(32))
    last_name = db.Column(db.String(32))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), unique=True, nullable=False)


@login.user_loader
def load_user(id):
    return Instructor.query.get(int(id))
