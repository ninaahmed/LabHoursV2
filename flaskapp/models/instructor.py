from flaskapp import db, login
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import check_password_hash

"""
    Database model to represent an Instructor
    in the "instructors" table. This class is
    also used as the "User" class for flask_login
    authentication
"""
class Instructor(UserMixin, db.Model):
    __tablename__ = "instructors"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(32))
    last_name = db.Column(db.String(32))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), unique=True, nullable=False)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

"""
    Allows the login manager to load the
    correct user from the database based
    on their ID
"""
@login.user_loader
def load_user(id):
    return Instructor.query.get(int(id))
