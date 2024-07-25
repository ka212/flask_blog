from flask_wtf import FlaskForm
import sqlite3
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])]) 
    submit = SubmitField('Update')

    def validate_username(self, username):
        conn = sqlite3.connect('site.db')
        c = conn.cursor()
        if username.data != current_user.username:
            c.execute("SELECT 1 FROM user WHERE username=?", (username.data,))
            if c.fetchone():
                raise ValidationError('That username is taken.')
        conn.close()

    def validate_email(self, email):
        conn = sqlite3.connect('site.db')
        c = conn.cursor()
        if email.data != current_user.email:
            c.execute("SELECT 1 FROM user WHERE email=?", (email.data,))
            if c.fetchone():
                raise ValidationError('That email is taken.')
        conn.close()


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        conn = sqlite3.connect('site.db')
        c = conn.cursor()
        c.execute("SELECT 1 FROM user WHERE username=?", (username.data,))
        if c.fetchone():
            raise ValidationError('that username is taken')
        conn.close()

    def validate_email(self, email):
        conn = sqlite3.connect('site.db')
        c = conn.cursor()
        c.execute("SELECT 1 FROM user WHERE email=?", (email.data,))
        if c.fetchone():
            raise ValidationError('that email is taken')
        conn.close()


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        conn = sqlite3.connect('site.db')
        c = conn.cursor()
        c.execute("SELECT 1 FROM user WHERE email=?", (email.data,))
        if not c.fetchone():
            raise ValidationError('there is no account with this email you muset rigester first')
        conn.close()


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset password')