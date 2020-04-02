from flaskapp import app, notifier
from flask import render_template, flash, url_for, redirect
from flaskapp.FormTest import EnterLineForm
from flaskapp import queue_handler

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
    queue = queue_handler.get_students()
    return render_template('display_line.html', title='Current Queue', queue=queue)

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