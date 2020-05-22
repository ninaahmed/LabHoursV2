from flaskapp import app, notifier, db, queue_handler, routes_helper, password_reset, options_text, options_urls
from flask import render_template, flash, url_for, redirect, request, g
from flaskapp.forms import EnterLineForm, LoginForm, RequestResetForm, ResetPasswordForm, InstructorForm
from flaskapp.student import Student
from flask_login import current_user, login_user, logout_user, login_required
from flaskapp.models.instructor import Instructor
from flaskapp.models.visit import Visit
from datetime import datetime
from werkzeug.urls import url_parse
from werkzeug.security import generate_password_hash
import validators
import json
import secrets

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
@app.route("/index", methods=['GET', 'POST'])
def homepage():
    return render_template('homepage.html', link = zoom_link)

@app.route("/join", methods=['GET', 'POST'])
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
       queue_is_open = routes_helper.handle_line_form(request, queue_is_open)

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
                if not user.is_active:
                    message = "This account is inactive."
                    return render_template('login.html', title='Sign In', form=form, link = zoom_link, message=message)
                login_user(user, remember=False)
                next_page = request.args.get('next')
                if not next_page or url_parse(next_page).netloc != '':
                    next_page = url_for('view_line')
                return redirect(next_page)
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
@login_required
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

@app.route('/clear', methods=['POST'])
def clear():
    if 'token' not in request.form:
        return json.dumps({'success':False}), 401, {'ContentType':'application/json'} 
    expected_token = app.config['CLEAR_TOKEN']
    if request.form['token'] != expected_token:
       return json.dumps({'success':False}), 401, {'ContentType':'application/json'} 
    queue_handler.clear()
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@app.route('/open', methods=['POST'])
def open():
    global queue_is_open
    if 'token' not in request.form:
        return json.dumps({'success':False}), 401, {'ContentType':'application/json'} 
    expected_token = app.config['OPEN_TOKEN']
    if request.form['token'] != expected_token:
       return json.dumps({'success':False}), 401, {'ContentType':'application/json'} 
    queue_is_open = True
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@app.route('/close', methods=['POST'])
def close():
    global queue_is_open
    if 'token' not in request.form:
        return json.dumps({'success':False}), 401, {'ContentType':'application/json'} 
    expected_token = app.config['CLOSE_TOKEN'];
    if request.form['token'] != expected_token:
        return json.dumps({'success':False}), 401, {'ContentType':'application/json'} 
    queue_is_open = False
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@app.route('/request_reset', methods=['GET', 'POST'])
def request_reset():
    form = RequestResetForm()
    message = ""
    if request.method == 'POST':
        if form.validate_on_submit():
            form_email = form.email.data
            user = Instructor.query.filter_by(email=form_email).first()
            if user is None:
                message = "Not a valid email address"
                return render_template('request_reset.html', form=form, message=message)
            else:
                # This is a valid user/email address
                password_reset.create_reset_request(user)
                return render_template('reset_message.html', title="Reset Request Made", body=f"Instructions for resetting your password have been sent to {form_email}")
        else:
            message = "Enter a valid email"

    return render_template('request_reset.html', form=form, message=message)

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    form = ResetPasswordForm()
    message = ''
    if 'token' in request.args:
        if request.method == 'POST':
            if form.validate_on_submit():
                if password_reset.update_password(request.args['token'], form.password.data):
                    return render_template('reset_message.html', title="Password reset", body="Your password was successfully updated")
                else:
                    return render_template('reset_message.html', title="Reset error", body="Your password could not be reset. The reset link used is no longer valid.")
            else:
                message = 'Both passwords must match'
        return render_template('reset_password.html', token=request.args['token'], form = form, message=message)
    else:
        return render_template('reset_message.html', title="Reset error", body="Malformed reset link. Token not present")

@app.route('/admin_panel', methods=['GET', 'POST'])
@login_required
def admin_panel():
    if current_user.is_admin:
        return render_template('admin_panel.html', instructors=Instructor.query.all())
    else:
        return render_template('reset_message.html', title="Admin Panel", body="Not authenticated, must be admin")


@app.route('/edit_instructor', methods=['GET', 'POST'])
@login_required
def edit_instructor():
    if current_user.is_admin:
        if 'id' not in request.args:
            return render_template('reset_message.html', title="Error", body="Missing instructor id")
        instr = Instructor.query.filter_by(id=request.args['id']).first()
        if request.method == 'GET':
            if instr is None:
                return render_template('reset_message.html', title="Error", body="Invalid instructor id")
            form = InstructorForm(first_name=instr.first_name, last_name=instr.last_name, email=instr.email, is_active=(instr.is_active != 0), is_admin=(instr.is_admin != 0))
            return render_template('edit_instructor.html', title="Edit Instructor", form=form, message='', id=instr.id)
        else:
            form = InstructorForm()
            if form.validate_on_submit():
                instr.first_name = form.first_name.data
                instr.last_name = form.last_name.data
                instr.email = form.email.data
                instr.is_active = 1 if form.is_active.data else 0
                instr.is_admin = 1 if form.is_admin.data else 0
                db.session.commit()
                return redirect('admin_panel')
            else:
                message = 'Enter a valid email address'
                return render_template('edit_instructor.html', title="Edit Instructor", form=form, message=message)
    else:
        return render_template('reset_message.html', title="Edit user", body="Not authenticated")

@app.route('/add_instructor', methods=['GET', 'POST'])
@login_required
def add_instructor():
    if current_user.is_admin:
        message = ''
        if request.method == 'GET':
            form = InstructorForm(is_active=True)
            return render_template('edit_instructor.html', title="Create Instructor", form=form, message=message)
        else:
            form = InstructorForm()
            if form.validate_on_submit():
                instr = Instructor()
                instr.first_name = form.first_name.data
                instr.last_name = form.last_name.data
                instr.email = form.email.data
                instr.is_active = 1 if form.is_active.data else 0
                instr.is_admin = 1 if form.is_admin.data else 0
                instr.password_hash = generate_password_hash(secrets.token_urlsafe(20))
                db.session.add(instr)
                db.session.commit()
                password_reset.new_user(instr)
                return redirect('admin_panel')
            else:
                message = 'Enter a valid email address'
    else:
        return render_template('reset_message.html', title="Edit user", body="Not authenticated")

"""
    401 User not authenticated
"""
@app.errorhandler(401)
def not_authenticated(error):
    return render_template('error_pages/401.html')

"""
    404 Page not found Error handler
"""
@app.errorhandler(404)
def page_not_found(error):
    return render_template('error_pages/404.html')