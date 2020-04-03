from flaskapp import app, notifier, db, FULL_URL, queue_handler
from flask import render_template, flash, url_for, redirect, request, g
from flaskapp.FormTest import EnterLineForm, LoginForm
from flaskapp.student import Student
from flask_login import current_user, login_user, logout_user
from flaskapp.models.instructor import Instructor
from flaskapp.models.visit import Visit
from datetime import datetime
import validators

"""
    This file contains all of the Flask routes
    for the app.
"""

orig_link = 'https://www.google.com'
zoom_link = 'https://www.google.com'

queue_is_open = False

@app.before_request
def load_user():
    g.full_url = FULL_URL 
    g.user = current_user

# the current main page where a student will send in their information
@app.route("/", methods=['GET', 'POST'])
def join():
    form = EnterLineForm()
    message = ""
    if not queue_is_open and request.method == 'POST':
        message = "Sorry, the queue was closed."
    else: 
        # go to the page that shows the people in the queue if you've submitted
        # a valid form
        if form.validate_on_submit():
            visit = Visit(eid=form.eid.data, time_entered=datetime.utcnow(), time_left=None, was_helped=0, instructor_id=None)
            db.session.add(visit)
            db.session.commit()
            s = Student(form.name.data, form.email.data, form.eid.data, visit.id)
            place = queue_handler.enqueue(s)
            flash(f'{form.name.data} has been added to the queue!', 'success')
            try:
                notifier.send_message(form.email.data, "Notification from 314 Lab Hours Queue", render_template("added_to_queue_email.html", place_str=get_place_str(place), student_name=form.name.data, remove_code="312-314"), 'html')
            except Exception as e:
                print(f"Failed to send email to {form.email.data}\n{e}")
            return redirect(url_for('view_line'))
        else:
            if len(form.errors) > 0:
                message = next(iter(form.errors.values()))[0]

    # render the template for submitting otherwise
    return render_template('enter_line.html', title='Join Line', form=form, link = zoom_link, queue_is_open=queue_is_open, message=message)

# prints out what the current queue looks like
@app.route("/line", methods=['GET', 'POST'])
def view_line():
    # A button was pressed on an entry in the line
    if request.method == 'POST' and current_user.is_authenticated:
       handle_line_form(request)

    queue = queue_handler.get_students()
    return render_template('display_line.html', title='Current Queue', queue=queue, user=current_user, link=zoom_link, queue_is_open=queue_is_open)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('view_line'))
    form = LoginForm()

    if form.validate_on_submit():
        user = Instructor.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            return redirect(url_for('login'))
        login_user(user, remember=False)
        return redirect(url_for('view_line'))
    return render_template('login.html', title='Sign In', form=form, link = zoom_link)

@app.route('/remove', methods=['GET', 'POST'])
def remove_student():
    message = ""
    # Form submitted to remove student
    if request.method == 'POST':
        s = queue_handler.remove_eid(request.form['eid'])
        if s is not None:
            v = Visit.query.filter_by(id=s.id).first()
            if v is not None:
                v.time_left = datetime.utcnow()
                v.was_helped = 0
                db.session.commit()
            else:
                print("Did not find visit in the database!")
            return redirect(url_for('view_line'))
        else:
            message = "EID not found in queue"
    return render_template('remove.html', message=message, link = zoom_link)

@app.route('/change_zoom', methods=['GET', 'POST'])
def change_zoom():
    global zoom_link
    message = ""

    if request.method == 'POST':
        if 'new' in request.form:
            temp = request.form['link']
            if validators.url(temp):
                zoom_link = temp
                message = "The link has been changed!"
            else:
                message = "Invalid URL :-/"
        elif 'reset' in request.form:
            zoom_link = orig_link
            message = "The link has been reset!"
    return render_template('change_zoom.html', message=message, link = zoom_link)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('join'))

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

"""
    Handle post requests in the view line page.
"""
def handle_line_form(request):
    global queue_is_open
    # Handle removing student
    if 'finished' in request.form or 'removed' in request.form:
        handle_remove(request)
    elif 'close' in request.form:
        queue_is_open = False
    elif 'open' in request.form:
        queue_is_open = True
        
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
    # Update visit entry in the database
    v = Visit.query.filter_by(id=uid).first()
    v.time_left = datetime.utcnow()
    if 'finished' in request.form:
        v.was_helped = 1
        v.instructor_id = current_user.id
    elif 'removed' in request.form:
        v.was_helped = 0
    # Write changes to database
    db.session.commit()
    # Notify runner-up in the queue
    s = queue_handler.peek_runner_up()
    if s is not None:
        try:
            notifier.send_message(s.email, "Notification from 314 Lab Hours Queue", render_template("up_next_email.html", student_name=s.name, remove_code="312-314"), 'html')
        except:
            print(f"Failed to send email to {s.email}")