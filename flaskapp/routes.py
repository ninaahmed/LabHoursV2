from flaskapp import app, notifier, db
from flask import render_template, flash, url_for, redirect, request, g
from flaskapp.FormTest import EnterLineForm, LoginForm
from flaskapp import queue_handler
from flaskapp.student import Student
from flask_login import current_user, login_user, logout_user
from flaskapp.models.instructor import Instructor
from flaskapp.models.visit import Visit
from datetime import datetime


"""
    This file will contain all of the Flask routes
    for the app.
"""

@app.before_request
def load_user():
    g.user = current_user

# the current main page where a student will send in their information
@app.route("/", methods=['GET', 'POST'])
def join():
    form = EnterLineForm()

    # go to the page that shows the people in the queue if you've submitted
    # a valid form
    if form.validate_on_submit():
        visit = Visit(eid=form.eid.data, time_entered=datetime.utcnow(), time_left=None, was_helped=0, instructor_id=None)
        db.session.add(visit)
        db.session.commit()
        s = Student(form.name.data, form.email.data, form.eid.data, visit.id)
        place = queue_handler.enqueue(s)
        flash(f'{form.name.data} has been added to the queue!', 'success')
        notifier.send_message(form.email.data, "Notification from Lab Hours Queue", render_template("email_template.html", queue_pos_string=get_place_str(place)), 'html')
        return redirect(url_for('view_line'))

    # render the template for submitting otherwise
    return render_template('enter_line.html', title='Join Line', form=form)

# prints out what the current queue looks like
@app.route("/line", methods=['GET', 'POST'])
def view_line():
    # A button was pressed on an entry in the line
    if request.method == 'POST':
        # Handle removing student
        uid = request.form['finished']
        queue_handler.remove(uid)
        v = Visit.query.filter_by(id=uid).first()
        v.time_left = datetime.utcnow()
        v.was_helped = 1
        v.instructor_id = current_user.id
        db.session.commit()

    queue = queue_handler.get_students()
    return render_template('display_line.html', title='Current Queue', queue=queue, user=current_user)

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
    else:
        print(f"not validated errors={form.errors}")
    return render_template('login.html', title='Sign In', form=form)

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
    if place >= 4:
        return f"{place}th"
    elif place == 1:
        return "1st"
    elif place == 2:
        return "2nd"
    elif place == 3:
        return "3rd"