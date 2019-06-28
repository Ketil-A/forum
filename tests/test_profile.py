import pytest
from flask import g, session
from flaskr.db import get_db

def test_profile(client, auth):
    auth.login()
    #Test that user profile exists
    assert client.get('/profile/test').status_code == 200


@pytest.mark.parametrize(('firstname', 'lastname','bio', 'userid'), (
    ('abc','def','ghijk',1),
))
def test_profile_update(app, client, auth, firstname, lastname, bio, userid):
    auth.login('test','test')
    response = client.post(
        '/profile/test/edit', data={'firstname': firstname, 'lastname': lastname, 'bio': bio}
    )
    #Test if redirected to profileView after password change.
    assert 'http://localhost/profile/test' == response.headers['Location']

    #Test that the profile was updated
    with app.app_context():
        profile = get_db().execute(
            "select * from profile where user_id = ?", (userid,)
        ).fetchone()
        assert profile['firstname'] == firstname
        assert profile['lastname'] == lastname
        assert profile['bio'] == bio