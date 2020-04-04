from flaskapp import app, notifier, db, queue_handler, routes_helper
from flask import render_template, flash, url_for, redirect, request, g
from flaskapp.FormTest import EnterLineForm, LoginForm
from flaskapp.student import Student
from flask_login import current_user, login_user, logout_user
from flaskapp.models.instructor import Instructor
from flaskapp.models.visit import Visit
from datetime import datetime
import validators

"""
    Handle post requests in the view line page.
    Will return a boolean indicating whether the line should be
    open (True) or closed (False).
"""
def handle_line_form(request, curr_open_state):
    # Handle removing student, the line's "open state" should
    # be unchanged.
    if 'finished' in request.form or 'removed' in request.form:
        handle_remove(request)
        return curr_open_state
    # Close the queue to new entries
    elif 'close' in request.form:
        return False
    # Open the queue to new entries
    elif 'open' in request.form:
        return True

"""
    Handles removing a student from the view queue
    page. This can be done either using the "Finish"
    button once a student is helped or the "Remove" button
    if a student is removed from the queue without being
    helped. Will notify new runner-up in the queue.
"""
def handle_remove(request):
    if 'finished' in request.form:
        uid = request.form['finished']
    elif 'removed' in request.form:
        uid = request.form['removed']
    queue_handler.remove(uid)
    # Update this visit entry in the database
    v = Visit.query.filter_by(id=uid).first()
    if v is not None:
        v.time_left = datetime.utcnow()
        if 'finished' in request.form:
            v.was_helped = 1
            v.instructor_id = g.user.id
        elif 'removed' in request.form:
            v.was_helped = 0
        # Write changes to database
        db.session.commit()
    else:
        print(f"Did not find entry for {uid} in the visits table.")
    # Notify runner-up in the queue
    s = queue_handler.peek_runner_up()
    if s is not None:
        try:
            notifier.send_message(s.email, "Notification from 314 Lab Hours Queue", 
            render_template("up_next_email.html", student_name=s.name, remove_code=s.eid), 'html')
        except:
            print(f"Failed to send email to {s.email}")

"""
    Formats a place in the queue with the appropriate suffix.
    i.e. 1 => "1st", 2 -> "2nd", etc
    Used in the email when someone joins the queue
"""
def get_place_str(place):
    place_str = str(place)
    if len(place_str) == 2 and place_str[0] == '1':
        return f"{place}th"
    elif place_str[-1] == '1':
        return f"{place}st"
    elif place_str[-1] == '2':
        return f"{place}nd"
    elif place_str[-1] == '3':
        return f"{place}rd"
    else:
        return f"{place}th"
