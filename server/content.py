from flask import (
    Blueprint, flash, g, render_template, redirect, request, url_for
)
from werkzeug.exceptions import abort 
import requests

from server.auth import login_required
from server.db import get_db
from server.strava import parse_auth_url, request_access_token

bp = Blueprint('content', __name__)


@bp.route('/')
def index():
    # get the data from the db, render it using a template
    return render_template('index.html')

@bp.route('/strava')
def get_strava_data():
    auth_url = "https://www.strava.com/oauth/authorize" + \
               "?client_id=60014&" + \
               "redirect_uri=http://127.0.0.1:5000/strava/auth&" + \
               "response_type=code&" + \
               "approval_prompt=auto&" + \
               "scope=read_all%2Cactivity%3Aread_all"

    return redirect(auth_url)

@bp.route('/strava/auth')
def strava_token_exchange():
    # at this point i need to parse the auth code and scope
    # check that the scope is what i need (if not redirect)
    # exchange auth code for access token
    code, scope = parse_auth_url(request.url) 
    request_access_token(code, 60014, client_secret)
    return render_template('index.html')