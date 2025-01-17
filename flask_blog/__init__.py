import os
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
app.config['SECRET_KEY'] = '152d42c61598e47a6bb0f0515464aabe'
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER']= 'smtp.googlemail.com'
app.config['MAIL_PORT']= 587
app.config['MAIL_USE_TLS']= True
app.config['MAIL_USERNAME']='kawtharmes@gmail.com'
app.config['MAIL_PASSWORD']='jteviphrxfpdepss'
mail = Mail(app)



from flask_blog.init_db import init_db, close_db
from flask_blog.users.routes import users
from flask_blog.posts.routes import posts
from flask_blog.main.routes import main

app.register_blueprint(users)
app.register_blueprint(posts)
app.register_blueprint(main)

init_db()
app.teardown_appcontext(close_db)