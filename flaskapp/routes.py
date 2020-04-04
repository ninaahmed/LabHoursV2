from flaskapp import app, notifier, db, queue_handler, routes_helper, options_text, options_urls
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

# The current Zoom link
zoom_link = options_urls[1] if len(options_urls) > 1 else 'https://www.utexas.instructure.com'

queue_is_open = False

@app.before_request
def load_user():
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
                notifier.send_message(form.email.data, "Notification from 314 Lab Hours Queue", 
                render_template("added_to_queue_email.html", place_str=routes_helper.get_place_str(place), 
                student_name=form.name.data, remove_code=form.eid.data), 'html')
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
    global queue_is_open
    # A button was pressed on an entry in the line
    if request.method == 'POST' and current_user.is_authenticated:
       queue_is_open = routes_helper.handle_line_form(request)

    queue = queue_handler.get_students()
    return render_template('display_line.html', title='Current Queue', queue=queue, user=current_user, link=zoom_link, queue_is_open=queue_is_open)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('view_line'))
    form = LoginForm()
    message = ""
    if request.method == 'POST':
        if form.validate_on_submit():
            user = Instructor.query.filter_by(email=form.email.data).first()
            if user is None or not user.check_password(form.password.data):
                message = "Incorrect email or password"
                return render_template('login.html', title='Sign In', form=form, link = zoom_link, message=message)
            else:
                login_user(user, remember=False)
                return redirect(url_for('view_line'))
        else:
            message = "Enter a valid email."
    return render_template('login.html', title='Sign In', form=form, link = zoom_link, message=message)

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
        if 'default' in request.form:
            index = int(request.form['zooms'])
            if index == 0:
                message = "Invalid choice :-/"
            else:
                zoom_link = options_urls[index]
                message = "The link has been changed!"
        elif 'new' in request.form:
            temp = request.form['link']
            if validators.url(temp):
                zoom_link = temp
                message = "The link has been changed!"
            else:
                message = "Invalid URL :-/"
    return render_template('change_zoom.html', message=message, link = zoom_link, options=options_text)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('join'))