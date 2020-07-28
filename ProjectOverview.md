# Lab Hours Queue Project Overview

For instructions on how to run the application with a development server, see the instructions in `setup/README.md`.

## Source Files

This project was developed in Python using Flask.

Instructor logins were handled using the `flask_login` library.

Form verification was handled using the `flask-wtf` library.

Connections with the database were handled using the `flask_sqlalchemy` library.

### The `flaskapp` Module

* `__init__.py` - Initializes the application by loading configuration files, initializing modules such as the databse and email notifier, and starting the Flask REST API.
* `routes.py` - Includes all of the flask routes, i.e. all the application entry points. Will accept and process requests.
* `routes_helper.py` - Provides helper procedures for processing the requests received in `routes.py`
* `queue_handler.py` - Maintains the queue of students.
* `student.py` - Contains a class to represent a Student in the queue.
* `forms.py` - Contains WTForm Form objects for the various forms on the site that need to be verified.
* `notifications.py` - Handles sending email notifications.
* `password_reset.py` - Handles password resetting behavior.
* `stats.py` - Generates csv files from database and generates various graphs.
* `models/instructor.py` - Provides a database model for a row in the instructor table.
* `models/visit.py` - Provides a database model for a row in the visit table.

### Other Python Files

* `labhoursqueue.py` - The main executable for the entire application. Will simply import the `flaskapp` module which initializes and runs the application.
* `edit_instructors.py` - A utility script for managing the `instructors` table in the database. This script allows for adding, modifying, and removing instructor entries.
* `edit_visits.py` - A utility script for managing the `visits` table in the database. This script allows for viewing the entries in the table and clearing the table.

## Database

This project uses an SQLite database and interactions with
the database are done with SQLAlchemy.

The database has two tables: `instructors` and `visits`.

The `instructors` table is used for storing account
information and credentials for the instructors.
This allows instructors to log in and have elevated
privileges for managing the queue, changing the Zoom link,
etc.

The `visits` table provides a log of all entries in the
queue. It is not used for representing the queue itself,
it only provides a historical listing of all the entries
in it. The entries in the `visits` table store the time
the student entered and left the queue, whether or not they
were helped, and which instructor helped them. We hope
this data could be used to analyze trends and identify
potential issues with how lab hours are being conducted.

## HTML & CSS

The Tailwind CSS framework was used for the the styling of
the site.

## Email

Whenever students join the line for lab hours, they will
receive an email notifying them that they've been entered
in line and what place in line they're at. The email will
also include their remove key (or EID) which was entered
on the join page (in case they forgot it).

Whenever a student is next to be helped in line, they will
receive another email informing them they've reached the
front of the queue. This should help students be more
prepared for when it is their turn to be helped by an
instructor.
