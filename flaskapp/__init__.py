from flask import Flask, g
from flaskapp.notifications import Notifier
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config.from_pyfile('config.cfg')

db = SQLAlchemy(app)
login = LoginManager(app)

# Create database tables if nonexistent
from flaskapp.models.instructor import *
from flaskapp.models.visit import *
db.create_all()
db.session.commit()

# Create an Email Notifications object to use throughout lifetime of program
notifier = Notifier(app.config['EMAIL_ACCOUNT'], app.config['EMAIL_PASSWORD'], app.config['EMAIL_SERVER'], app.config['EMAIL_SERVER_PORT'])

# Initialize Zoom links from file
COMMENT_PREFIX = '#' 
"""
    This file should have the format:
    Description of URL1
    URL1
    Description of URL2
    URL2
    ...
    Lines which begin with '#' are ignored, can
    be used as comments in the file
"""

# Will store the Zoom links in memory
options_text = ["Click Here for Default Links"]
options_urls = ["default url"]
index = 0

# Tries to open and read the Zoom links file
try:
    with open(app.config['ZOOM_LINKS_FILE']) as input_file:
        lines = [ line.strip() for line in input_file.readlines() ]
        for line in lines:
            # Skip empty lines and comments
            if line and line[0] != COMMENT_PREFIX:
                if index % 2 == 0:
                    options_text.append(line)
                else:
                    options_urls.append(line)
                line = input_file.readline().strip()
                index += 1
except Exception as e:
    print(f"Failed to initialize zoom links. Malformed or missing file: {app.config['ZOOM_LINKS_FILE']}")
    print(e)
    exit(1)

# Create a Debug admin account
# debug_admin = Instructor(first_name="Debug", last_name="User",
#     email=app.config['DEBUG_ADMIN_EMAIL'],
#     password_hash=generate_password_hash(app.config['DEBUG_ADMIN_PASSWORD']),
#     is_active = 1, is_admin = 1)

# db.session.add(debug_admin)
# db.session.commit()

from flaskapp import routes
