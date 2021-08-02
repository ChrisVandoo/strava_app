from flask import (
    Blueprint, render_template, redirect, request, session
)

from getpass import getpass

from server.db import get_db
from server.strava import Auth, Strava

bp = Blueprint('content', __name__, cli_group=None)


@bp.route('/')
def index():
    # get the data from the db, render it using a template
    return render_template('index.html')

@bp.route('/strava')
def get_strava_data():  
    user = session.get("user_id")
    auth = Auth(user)
    print("Authenticated? ", auth.is_auth())

    if auth.is_auth():
        token = auth.get_token()
        print("ready to query Strava!", token)
        # use the token to request some data from Strava
        strava = Strava(token)
        activities = strava.list_all_activities()
        print(activities)

    else:
        url = auth.get_auth_url()
        return redirect(url)

    return redirect('/')
    

@bp.route('/strava/auth')
def strava_token_exchange():
    # initial OAuth authentication for Strava (should only be done once/user)
    user = session.get("user_id")
    strava_auth = Auth(user)

    strava_auth.init_auth(request.url)
    if strava_auth.is_auth():
        print("successfully authenticated!")
        token = strava_auth.get_token()

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

    db.commit()
    db.close()