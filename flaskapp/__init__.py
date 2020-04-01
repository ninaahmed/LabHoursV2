from flask import Flask
from flaskapp.notifications import Notifier

app = Flask(__name__)
app.config['SECRET_KEY'] = '60e9d370211350d549959ff535c06f13'

# Credentials File
EMAIL_CREDENTIALS_FILE = "testing.cred"
# Create an Email Notifications object to use throughout lifetime of program
notifier = Notifier(EMAIL_CREDENTIALS_FILE)

from flaskapp import routes