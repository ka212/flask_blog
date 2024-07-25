from flask import render_template, request, Blueprint
from datetime import datetime
import sqlite3

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/home')
def home():
    conn = sqlite3.connect('site.db')
    c = conn.cursor()
    c.execute("""
        SELECT p.*, u.username, u.email, u.image_file
        FROM post p
        JOIN user u ON p.user_id = u.id
    """)
    posts = c.fetchall()
    conn.close()
    post_data = []
    for post in posts:
        post_dict = {
            'id': post[0],
            'title': post[1],
            'date_posted': datetime.strptime(post[2], '%Y-%m-%d %H:%M:%S.%f'),  # parse the string into a datetime object
            'content': post[3],
            'user_id': post[4],
            'username': post[5],
            'email': post[6],
            'image_file': post[7]
        }
        post_data.append(post_dict)
    return render_template('home.html', posts=post_data)

@main.route('/about')
def about():
    return render_template('about.html', title='About')