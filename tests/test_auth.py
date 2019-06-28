import pytest
from flask import g, session
from flaskr.db import get_db


def test_register(client, app):
    # test that viewing the page renders without template errors
    assert client.get('/auth/register').status_code == 200

    # test that successful registration redirects to the login page
    response = client.post(
        '/auth/register', data={'username': 'a', 'password': 'a', 'email': 'a@a.a'}
    )
    assert 'http://localhost/auth/login' == response.headers['Location']

    # test that the user was inserted into the database
    with app.app_context():
        assert get_db().execute(
            "select * from user where username = 'a'",
        ).fetchone() is not None


@pytest.mark.parametrize(('username', 'password','email', 'message'), (
    ('','','', b'Username is required.'),
    ('a','','', b'Password is required.'),
    ('test', 'test', 'test@test.no', b'already registered'),
))
def test_register_validate_input(client, username, password, email, message):
    response = client.post(
        '/auth/register',
        data={'username': username, 'password': password, 'email': email}
    )
    assert message in response.data


def test_login(client, auth):
    # test that viewing the page renders without template errors
    assert client.get('/auth/login').status_code == 200

    # test that successful login redirects to the index page
    response = auth.login()
    assert response.headers['Location'] == 'http://localhost/'

    # login request set the user_id in the session
    # check that the user is loaded from the session
    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'test'


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'Incorrect username.'),
    ('test', 'a', b'Incorrect password.'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session

def test_password_change(client, auth):
    auth.login()
    response = client.post(
        '/auth/password',
        data={'oldpassword': 'test', 'password': 'test2', 'confirmpassword': 'test2'}
    )
    #Test if redirected to index after password change.
    assert 'http://localhost/' == response.headers['Location']

@pytest.mark.parametrize(('oldpassword', 'newpassword', 'confirmpassword', 'message'), (
    ('wrongpass', 'test2','test2', b'Incorrect password.'),
    ('test', '','', b'Password is required.'),
    ('test', 'match','mismatch', b'Passwords do not match.'),
))
def test_change_password_validation(client, auth, oldpassword, newpassword, confirmpassword, message):
    auth.login()
    response = client.post(
        '/auth/password',
        data={'oldpassword': oldpassword, 'password': newpassword, 'confirmpassword': confirmpassword}
    )
    assert message in response.data


def test_change_email(client, auth):
    auth.login()
    response = client.post(
        '/auth/email',
        data={'email': 'testchange@test.no'}
    )
    #Test if redirected to index after email change.
    assert 'http://localhost/' == response.headers['Location']

@pytest.mark.parametrize(('email', 'message'), (
    ('', b'Email is required'),
    ('test', b'Invalid email.'),
))
def test_change_email_validation(client, auth, email, message):
    auth.login()
    response = client.post(
        '/auth/email',
        data={'email': email}
    )
    assert message in response.data
