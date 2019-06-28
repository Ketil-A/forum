import functools
import re

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


def login_required(view):
    """View decorator that redirects anonymous users to the login page."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    """If a user id is stored in the session, load the user object from
    the database into ``g.user``."""
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/register', methods=('GET', 'POST'))
def register():
    """Register a new user.

    Validates that the username is not already taken. Hashes the
    password for security.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email'] #TODO? (Nice to have) send confirmation email
        db = get_db()
        c = db.cursor()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif not email:
            error = 'Password is required.'
        elif not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email):
            error = 'Invalid email.'
        elif c.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {0} is already registered.'.format(username)

        if error is None:
            # the name is available, store it in the database and go to
            # the login page
            c.execute(
                'INSERT INTO user (username, password, email) VALUES (?, ?, ?)',
                (username, generate_password_hash(password), email)
            )
            user_id = c.lastrowid
            c.execute(
                'INSERT INTO profile (user_id) VALUES (?)',
                (user_id,)
            )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    """Log in a registered user by adding the user id to the session."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            # store the user id in a new session and return to the index
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    """Clear the current session, including the stored user id."""
    session.clear()
    return redirect(url_for('index'))

@bp.route('/password', methods=('GET', 'POST'))
@login_required
def change_password():
    if request.method == 'POST':
        oldpassword = request.form['oldpassword']
        password = request.form['password']
        confirmpassword = request.form['confirmpassword'] #TODO: Move to clientside
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE id = ?', (g.user['id'],)
        ).fetchone()

        if not check_password_hash(user['password'], oldpassword):
            error = 'Incorrect password.'
        elif not password:
            error = 'Password is required.'
        elif password != confirmpassword:
            error = 'Passwords do not match.'
        if error is None:
            db = get_db()
            db.execute(
                'UPDATE user SET password = ? WHERE id = ?',
                (generate_password_hash(password), g.user['id'])
            )
            db.commit()
            flash('Password changed successfully.')
            return redirect(url_for('index'))
        flash(error)
    return render_template('auth/password.html')

@bp.route('/email', methods=('GET', 'POST'))
@login_required
def change_email():
    if request.method == 'POST':
        email = request.form['email']
        db = get_db()
        error = None

        if not email:
            error = 'Email is required'
        elif not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email):
            error = 'Invalid email.'

        if error is None:
            db = get_db()
            db.execute(
                'UPDATE user SET email = ? WHERE id = ?',
                (email, g.user['id'])
            )
            db.commit()
            flash('Email changed successfully')
            return redirect(url_for('index'))
        flash(error)
    return render_template('auth/email.html', )
