from flaskapp import app, notifier
from flask import render_template, flash, url_for, redirect, request
from flaskapp.FormTest import EnterLineForm, LoginForm
from flaskapp import queue_handler
from flask_login import current_user, login_user
from flaskapp.models.instructor import Instructor

"""
    This file will contain all of the Flask routes
    for the app.
"""


# the current main page where a student will send in their information
@app.route("/", methods=['GET', 'POST'])
def join():
    form = EnterLineForm()

    # go to the page that shows the people in the queue if you've submitted
    # a valid form
    if form.validate_on_submit():
        flash(f'{form.name.data} has been added to the queue!', 'success')
        place = queue_handler.enqueue(form.name.data, form.email.data, form.eid.data)
        notifier.send_message(form.email.data, "Notification from Lab Hours Queue", render_template("email_template.html", queue_pos_string=get_place_str(place)), 'html')
        return redirect(url_for('view_line'))

    # render the template for submitting otherwise
    return render_template('enter_line.html', title='Join Line', form=form)

# prints out what the current queue looks like
@app.route("/line", methods=['GET', 'POST'])
def view_line():
    if request.method == 'POST':
        queue_handler.remove(request.form['finished'])
    queue = queue_handler.get_students()
    return render_template('display_line.html', title='Current Queue', queue=queue)

@app.route('/login', methods=['GET', 'POST'])
def login():
    print("in login")
    if current_user.is_authenticated:
        return redirect(url_for('view_line'))
    print("after if")
    form = LoginForm()
    print(f"email = {form.email.data}, password = {form.password.data}")

    if form.validate_on_submit():
        user = Instructor.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            print('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=False)
        return redirect(url_for('view_line'))
    else:
        print(f"not validated errors={form.errors}")
    return render_template('login.html', title='Sign In', form=form)

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