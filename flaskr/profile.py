from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('profile', __name__, url_prefix='/profile')

def get_profile(id): #TODO profile image?
    profile = get_db().execute(
        'SELECT *'
        ' FROM profile'
        ' WHERE user_id = ?',
        (id,)
    ).fetchone()

    return profile

def get_user(username):
    user = get_db().execute(
        'SELECT u.id, username, email'
        ' FROM user u'
        ' WHERE u.username = ?',
        (username,)
    ).fetchone()

    if user is None:
        abort(404, "User '{0}' doesn't exist.".format(username))
    return user

@bp.route('/<username>/')
def viewProfile(username):
    user = get_user(username)
    profile = get_profile(user['id'])
    return render_template('profile/view.html', profile=profile, user=user)

@bp.route('/<username>/edit', methods=('GET', 'POST'))#Edit profile, require access
@login_required
def editProfile(username):
    if username != g.user['username']:
        abort(403)
    if request.method == 'POST':
        #TODO handle user profile form, then refresh.
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        bio = request.form['bio']
        #TODO add more profile options
        db = get_db()
        db.execute(
            'UPDATE profile SET firstname = ?, lastname = ?, bio = ?'
            'WHERE user_id = ?',
            (firstname, lastname, bio, g.user['id'])
        )
        db.commit()
        return redirect(url_for('profile.viewProfile', username=username))
    user = get_user(username)
    profile = get_profile(user['id'])
    return render_template('profile/edit.html', profile=profile, user=user)