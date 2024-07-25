from flask import (render_template, url_for, flash, redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
import sqlite3
from datetime import datetime
from .forms import PostForm

posts = Blueprint('posts', __name__)

@posts.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        conn = sqlite3.connect('site.db')
        c = conn.cursor()
        c.execute("INSERT INTO post (title, date_posted, content, user_id) VALUES (?,?,?,?)",
                  (form.title.data, datetime.utcnow(), form.content.data, current_user.id))
        conn.commit() 
        conn.close()
        flash('Your Post has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='New Post', form=form)

@posts.route("/post/<int:post_id>")
def post(post_id):
    conn = sqlite3.connect('site.db')
    c = conn.cursor()
    c.execute("SELECT post.id, post.title, post.date_posted, post.content, post.user_id, user.username, user.email, user.image_file FROM post INNER JOIN user ON post.user_id = user.id WHERE post.id=?", (post_id,))
    post_data = c.fetchone()
    conn.close()
    if post_data is None:
        abort(404)

    class Post:
        def __init__(self, data):
            self.id = data[0]
            self.title = data[1]
            self.date_posted = data[2]
            self.content = data[3]
            self.user_id = data[4]
            self.username = data[5]
            self.email = data[6]
            self.image_file = data[7]
            self.author = data[4] 


    post = Post(post_data)
    return render_template('post.html', title=post.title, post=post, legend='New Post')


@posts.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    conn = sqlite3.connect('site.db')
    c = conn.cursor()
    c.execute("SELECT post.id, post.title, post.date_posted, post.content, post.user_id, user.username, user.email, user.image_file FROM post INNER JOIN user ON post.user_id = user.id WHERE post.id=?", (post_id,))
    post_data = c.fetchone()
    conn.close()
    if post_data is None:
        abort(404)
    if post_data[4] != current_user.id:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        conn = sqlite3.connect('site.db')
        c = conn.cursor()
        c.execute("UPDATE post SET title=?, date_posted=?, content=? WHERE id=?", 
                  (form.title.data, datetime.utcnow(), form.content.data, post_id))
        conn.commit()
        conn.close()
        flash('Your Post has been updated!', 'success')
        return redirect(url_for('posts.post', post_id=post_id))
    elif request.method == 'GET':
        form.title.data = post_data[1]
        form.content.data = post_data[3]
    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')


@posts.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    conn = sqlite3.connect('site.db')
    c = conn.cursor()
    c.execute("SELECT post.id, post.title, post.date_posted, post.content, post.user_id, user.username, user.email, user.image_file FROM post INNER JOIN user ON post.user_id = user.id WHERE post.id=?", (post_id,))
    post_data = c.fetchone()
    if post_data is None:
        abort(404)
    if post_data[4] != current_user.id:
        abort(403)
    c.execute("DELETE FROM post WHERE id=?", (post_id,))
    conn.commit() 
    conn.close() 
    flash('Your Post has been deleted!', 'success')
    return redirect(url_for('main.home'))