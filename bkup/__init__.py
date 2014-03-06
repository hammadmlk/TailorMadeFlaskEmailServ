# -*- coding: utf-8 -*-
"""
    tailormade
    ~~~~~~~~~
    
    Initiates the app

    :copyright: (c) 2013 by Saeed Abdullah.

"""

from flask import Flask
import sqlite3
from flask import g
from itsdangerous import URLSafeTimedSerializer
import flask_login

# Creates the app
app = Flask(__name__)

# Loads default config
import default_config
app.config.from_object(default_config)
#app.config.from_envvar('YOURAPPLICATION_SETTINGS')

# Database
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE_PATH'])
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# Password
import passlib
from passlib.context import CryptContext
pwd_context = CryptContext(
    schemes=["pbkdf2_sha512"],

    # vary rounds parameter randomly when creating new hashes...
    all__vary_rounds = 0.1,

    # Previous value was 8000, but, given the number of logins
    # I am reducing it.
    pbkdf2_sha512__default_rounds = 800,
    )

app.config['pwd_context'] = pwd_context

# login
app.login_serializer = URLSafeTimedSerializer(app.secret_key, salt="API_LOGIN")
login_manager = flask_login.LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "login"
login_manager.init_app(app)

@login_manager.user_loader
def login_manager_user_loader(useremail):
    u = load_user(useremail)
    if u:
        return UserWrapper(u)
    return None

def load_user(useremail):
    return query_db("select * from tailormade_user where useremail = ?", [useremail], one=True)

@login_manager.token_loader
def load_tokenized_user(token):
    """
    Provides `token_loader` callback for flask_login.

    :param token: The token from :func: `get_auth_token`
        and uses :func: `get_authenticated_user` for authentication.

    :returns:
        - Instance of :class:`UserWrapper`.
        - `None`, if the user can't be authenticated or any exception has been
        raised.
    """
    try:
        u_name, u_pass = app.login_serializer.loads(token,
                max_age=app.config["SESSION_DURATION"])
        u = load_user(u_name)
        if u['password'] == u_pass:
            return UserWrapper(u)
    except:
        app.logger.exception('Error in loading tokenizer user:')

    return None

class UserWrapper(flask_login.UserMixin):
    """
    Thin wrapper-class for User class used for Flask-Login protocol.

    """
    def __init__(self, u):
        self._user = u

    def get_id(self):
        """
        Returns the id of the document.

        This is a callback function that is being used by `flask_login`.
        """
        return self._user['useremail']

    def get_auth_token(self):
        """
        Creates the authenicated token for the user object.

        For use of the token see :func:`load_tokenized_user`.

        :returns:
            A encrypted string of user id and password. So, in case,
            the password has been changed, the token would be invalid.
        """

        data = [self.get_id(), self._user['password']]
        return app.login_serializer.dumps(data)

import api
