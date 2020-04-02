from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Email

class EnterLineForm(FlaskForm):
    name = StringField('Name', 
        validators=[DataRequired(), Length(min=2, max=30)])
    email = StringField('Email',
        validators=[DataRequired(), Email()])
    eid = StringField('EID',
        validators=[DataRequired()])
    submit = SubmitField('Join the Queue!')

class LoginForm(FlaskForm):
    email = StringField('Email',
        validators=[])
    password = PasswordField('Password',
        validators=[])
    submit = SubmitField('Sign In')