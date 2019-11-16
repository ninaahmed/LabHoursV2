from flask import Flask, render_template, url_for
from FormTest import EnterLineForm
app = Flask(__name__)

app.config['SECRET_KEY'] = '60e9d370211350d549959ff535c06f13'

@app.route("/")
def join():
    form = EnterLineForm()
    return render_template('enter_line.html', title='Join Line', form=form)

if __name__ == "__main__":
    app.run()