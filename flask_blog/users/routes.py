from flask import render_template, url_for, flash, redirect, request, Blueprint
import sqlite3
from flask_login import login_user, current_user, logout_user, login_required
from flask_blog import bcrypt
from flask_blog.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                   RequestResetForm, ResetPasswordForm)
from flask_blog.users.utils import save_picture, send_reset_email
from flask_blog.init_db import User, get_db


users = Blueprint('users', __name__)

@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('users.login'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        db = get_db()
        c = db.cursor()
        c.execute(
            "INSERT INTO user (username, email, image_file, password) VALUES (?,?,?,?)",
            (form.username.data, form.email.data, 'default.jpg', hashed_password),
        )
        db.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)

@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        conn = sqlite3.connect('site.db')
        c = conn.cursor()
        c.execute("SELECT * FROM user WHERE email=?", (form.email.data,))
        user_data = c.fetchone()
        if user_data and bcrypt.check_password_hash(user_data[4], form.password.data):
            user_obj = User(id=user_data[0], username=user_data[1], image_file=user_data[2], email=user_data[3], password=user_data[4])
            login_user(user_obj)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
        conn.close()
    return render_template('login.html', title='Login', form=form)

@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))



@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    conn = sqlite3.connect('site.db')
    c = conn.cursor()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            c.execute("UPDATE user SET image_file=? WHERE id=?", (picture_file, current_user.id))
        c.execute("UPDATE user SET username=?, email=? WHERE id=?", (form.username.data, form.email.data, current_user.id))
        conn.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        c.execute("SELECT username, email FROM user WHERE id=?", (current_user.id,))
        user_data = c.fetchone()
        form.username.data = user_data[0]
        form.email.data = user_data[1]
    image_file = url_for('static', filename='profil_pics/' + current_user.image_file)
    conn.close()
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)
    
@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        conn = sqlite3.connect('site.db')
        c = conn.cursor()
        c.execute("SELECT * FROM user WHERE email=?", (form.email.data,))
        user = c.fetchone()
        if user:
            send_reset_email(user)
            flash('An email has been sent with instructions to reset your password.', 'info')
            return redirect(url_for('users.login'))
        else:
            flash('That email does not exist in our database.', 'warning')
        conn.close()
    return render_template('reset_request.html', title='Reset Password', form=form)

@users.route('/reset/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        conn = sqlite3.connect('site.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE user SET password =? WHERE id =?", (hashed_password, user.id))
        conn.commit()
        conn.close()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)