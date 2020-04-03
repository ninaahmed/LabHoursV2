from flask import Flask, g
from flaskapp.notifications import Notifier
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = '60e9d370211350d549959ff535c06f13'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///labhours.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

login = LoginManager(app)

# Credentials File
EMAIL_CREDENTIALS_FILE = "testing.cred"
# Create an Email Notifications object to use throughout lifetime of program
notifier = Notifier(EMAIL_CREDENTIALS_FILE)

# Full Link to Website
FULL_URL = "http://314.consulting"

from flaskapp import routes
