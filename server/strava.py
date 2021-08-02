from urllib.parse import urlparse, parse_qs
from requests import post
from time import time

from server.db import get_db 

class Auth:
    # wrapper for authentication with Strava
    _client_id=60014

    def __init__(self, user):
        self._db = get_db() 
        self._user = user

        self._access_token=""
        self._refresh_token=""
        self._expires_at=0
        self._athlete={}

        self._temp_code=""
        self._scope=""

        self._client_secret = self._load_client_secret()

        # attempts to load auth config from database, return T or F
        self._authenticated=self._load_saved_auth()

    def get_token(self):
        # return a valid access token that can be used to query the Strava API
        if not self._authenticated:
            return ""

        # check that the token isn't expired
        if self._check_token():
            return self._access_token
        else:
            # if expired, request a new one             
            response = self._request_access_token({
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "grant_type": "refresh_token",
                "refresh_token": self._refresh_token
            })
            self._parse_auth_response(response)
            self._save_auth
            return self._access_token
            
    
    def is_auth(self):
        # indicates that a refresh_token and access_token have been loaded from the DB
        return self._authenticated

    def get_auth_url(self):
        # return the auth url required for initial authorization
        return "https://www.strava.com/oauth/authorize" + \
               "?client_id=60014&" + \
               "redirect_uri=http://127.0.0.1:5000/strava/auth&" + \
               "response_type=code&" + \
               "approval_prompt=auto&" + \
               "scope=read_all%2Cactivity%3Aread_all"
    
    def init_auth(self, auth_url):
        # setup auth things the first time around
        self._parse_auth_url(auth_url)

        if self._valid_scope():
            response = self._request_access_token({
                    "client_id":self._client_id,
                    "client_secret":self._client_secret,
                    "code":self._temp_code,
                    "grant_type":"authorization_code"
                })
            self._parse_auth_response(response)
            self._save_auth()
            self._authenticated = True 
    
    def _parse_auth_response(self, response):
        if response is not None:
            self._access_token = response.get("access_token")
            self._refresh_token = response.get("refresh_token")
            self._expires_at = response.get("expires_at")

    def _parse_auth_url(self, url):
        # parses auth url for the temporary auth code and the scope
        args = urlparse(url) 
        query_string = parse_qs(args[4])

        if "error" in query_string:
            self._temp_code, self._scope  = "", ""
        else:
            self._temp_code, self._scope  = query_string.get("code", ""), query_string.get("scope", "")
    
    def _valid_scope(self):
        # check the scope of the permissions given
        if self._scope == "":
            return False
        
        scopes = self._scope[0].split(",")

        if "activity:read_all" in scopes:
            return True 
        
        return False
    
    def _load_saved_auth(self):
        row = self._db.execute('SELECT * FROM auth WHERE id = ?', (self._user,)).fetchone()
        if row is None:
            return False
        else:
            self._access_token, self._refresh_token, self._expires_at = row["access_token"], row["refresh_token"], row["expires_at"]
            return True
    
    def _save_auth(self):
        exists = False 

        # check if this user has authenticated before
        if self._db.execute('SELECT id FROM auth WHERE id = ?', (self._user,)).fetchone() is not None:
            exists = True
        
        if exists:
            self._db.execute(
                'UPDATE auth SET (expires_at, refresh_token, access_token) VALUES (?, ?, ?) WHERE id = ?',
                (self._expires_at, self._refresh_token, self._access_token, self._user)
        )
        else:
            self._db.execute(
                'INSERT INTO auth (id, expires_at, refresh_token, access_token) VALUES (?, ?, ?, ?)',
                (self._user, self._expires_at, self._refresh_token, self._access_token)
            )
        self._db.commit()

    def _check_token(self):
        # check that the refresh_token hasn't expired and won't expire in the next 15 minutes (900 seconds)
        if int(time()) < (self._expires_at + 900):
            return True 
        return False
    
    def _request_access_token(self, data):
        r = post(
            url="https://www.strava.com/oauth/token",
            data=data 
        )
        return r.json()

    def _load_client_secret(self):
        # NOTE: the secret must be named 'strava_app' for this to work
        secret = self._db.execute(
            'SELECT * FROM client_secret WHERE secret_name = ?',
            ("strava_app",)
        ).fetchone()
        return (secret["secret_value"])

