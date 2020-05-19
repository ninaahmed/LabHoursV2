from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Email, EqualTo

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
        validators=[DataRequired(), Email()])
    password = PasswordField('Password',
        validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send Reset Instructions')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New password', validators=[
        DataRequired(),
        EqualTo('confirm', message='The two passwords do no match')
    ])
    confirm = PasswordField('Confirm new password')
    submit = SubmitField('Reset Password')