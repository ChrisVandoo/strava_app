import os
import tempfile 

import pytest 

from server import create_app
from server.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')

@pytest.fixture
def app():
    db_fd, dp_path = tempfile.mkstemp()
    app = create_app({'TESTING': True, 'DATABASE': dp_path})

    
    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)
    
    yield app 
    
    os.close(db_fd)
    os.unlink(dp_path)

@pytest.fixture
def client(app):
    # used to make requests to the app without actually running the server
    return app.test_client()

@pytest.fixture
def runner(app):
    # used to call Click commands registered with the app
    return app.test_cli_runner()

class AuthActions(object):
    """
    Since most functionality requires the user to login, this class factors out
    the steps required to login so that things can happen for a given test.
    """

    def __init__(self, client):
        self._client = client 
    
    def login(self, username="test", password="test"):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('auth/logout')

@pytest.fixture
def auth(client):
    return AuthActions(client)