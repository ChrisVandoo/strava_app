import calendar
from flask import (
    Blueprint, render_template, redirect, request, session
)

from getpass import getpass

from server.db import get_db
from server.strava import Auth, Strava
from server.data import is_data_in_db, save_data
from server.datahandler import DataHandler

bp = Blueprint('content', __name__, cli_group=None)


@bp.route('/')
def index():
    # get the data from the db, render it using a template
    return render_template('index.html')

@bp.route('/chart')
def chart():
    print("chart was called!")
    month = 1
    if request.args:
        month = int(request.args["months"])     
    
    dh = DataHandler(session.get("user_id"))
    data = dh.get_runs_for_month(month)
    return render_template('chart.html', data=data, month=calendar.month_name[month])

@bp.route('/chart_data')
def chart_data():
    print("chart_data was called")
    month = 1
    if request.args:
        month = int(request.args["months"])     
    
    dh = DataHandler(session.get("user_id"))
    data = dh.get_runs_for_month(month)

    return data

@bp.route('/strava')
def get_strava_data():  
    user = session.get("user_id")
    auth = Auth(user)
    print("Authenticated? ", auth.is_auth())

    if not auth.is_auth():
        url = auth.get_auth_url()
        return redirect(url)
    
    if not is_data_in_db(user):
        print("Getting data from Strava...")
        token = auth.get_token()
        strava = Strava(token)
        data = strava.get_all_activities()

        # save the data to the database
        save_data(data, user)
    else:
        print("Strava data already in the database!")

    return redirect('/chart')
    

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