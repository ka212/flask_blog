import sqlite3
from itsdangerous import Serializer as Serializer
from flask import g
from flask_blog import login_manager, app
from flask_login import UserMixin



class User(UserMixin): #UserMixin une extension de Flask qui gère l'authentification des utilisateurs.
    def __init__(self, id, username,image_file, email, password):
        self.id = id
        self.username = username
        self.email = email  
        self.image_file = image_file
        self.password = password

    
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        
        conn = sqlite3.connect('site.db')
        c = conn.cursor()
        c.execute("SELECT * FROM user WHERE id=?", (user_id,))
        user = c.fetchone()
        conn.close()
        if user:
            return User(id=user[0], username=user[1], email=user[2],image_file=user[3], password=user[4])
        return None

    
@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    user = db.execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
    if user is None:
        return None
    return User(user['id'], user['username'],user['image_file'], user['email'], user['password'])

DATABASE = 'site.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    with app.app_context():
        db = get_db()
        if not db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user'").fetchone():
            with app.open_resource('schema.sql', mode='r') as f:  #opens the schema script file (schema.sql) in read mode
                db.cursor().executescript(f.read())
            db.commit()
    
@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()