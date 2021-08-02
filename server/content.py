from flask import (
    Blueprint, flash, g, render_template, redirect, request, url_for, session
)
import requests
import click
from getpass import getpass

from server.db import get_db
from server.strava import Auth

bp = Blueprint('content', __name__, cli_group=None)


@bp.route('/')
def index():
    # get the data from the db, render it using a template
    return render_template('index.html')

@bp.route('/strava')
def get_strava_data():  
    return redirect("https://www.strava.com/oauth/authorize" + \
               "?client_id=60014&" + \
               "redirect_uri=http://127.0.0.1:5000/strava/auth&" + \
               "response_type=code&" + \
               "approval_prompt=auto&" + \
               "scope=read_all%2Cactivity%3Aread_all" )

@bp.route('/strava/auth')
def strava_token_exchange():
    # at this point i need to parse the auth code and scope
    # check that the scope is what i need (if not redirect)
    # exchange auth code for access token
    user = session.get("user_id")
    strava_auth = Auth(user)

    strava_auth.init_auth(request.url)
    if strava_auth.is_auth():
        print("successfully authenticated!")
        token = strava_auth.get_token()

    print(token)
    test_db(user)
    return redirect('/')


def test_db(user_id):
    db = get_db()
    stuff = db.execute(
        'SELECT * FROM auth WHERE id = ?', (user_id,)
    ).fetchone()

    print(stuff.keys())
    for thing in stuff:
        print(thing)


@bp.cli.command('load-secret')
def load_secret_command():
    """Loads a client secret into the db"""
    db = get_db()
    secret_name = input("enter secret_name: ").strip()
    secret_value = getpass(prompt="enter secret: ").strip()

    db.execute(
        'INSERT INTO client_secret (secret_name, secret_value) VALUES (?, ?)',
        (secret_name, secret_value,)
    )

