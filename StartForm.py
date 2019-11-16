from flask import Flask, render_template, flash
from FormTest import EnterLineForm
import queue_handler
app = Flask(__name__)

app.config['SECRET_KEY'] = '60e9d370211350d549959ff535c06f13'

# the current main page where a student will send in their information
@app.route("/", methods=['GET', 'POST'])
def join():
    form = EnterLineForm()
    if form.validate_on_submit():
        flash(f'{form.name.data} has been added to the queue!', 'success')
        queue_handler.add_to_queue(form.name.data, form.email.data, form.eid.data)
    return render_template('enter_line.html', title='Join Line', form=form)

# prints out what the current queue looks like
@app.route("/line", methods=['GET'])
def view_line():
    queue = queue_handler.get_students()
    return render_template('display_line.html', title='Current Queue', queue=queue)

if __name__ == "__main__":
    app.run()