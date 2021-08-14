"""
Process Strava activity data.

Schema (save this to a Database):
{
    "name": <activity title>
    "distance": <in meters>
    "moving_time": <in seconds>
    "elapsed_time": <in seconds>
    "total_elevation_gain": <in meters>
    "type": <Run | Bike | Hike etc.>
    "id": <activity id>
    "start_date": <date when activity started>
    "kudos_count": <# of kudos on activity>
}

"""

import sqlite3
from server.db import get_db

def save_data(data, user_id):
    """
    Takes raw data from Strava, parses the important fields and saves it to a database.

    :param: data - list of pages of data from strava
    """
    data_db = DataBase()

    for page in data:
        for raw_activity in page:
            activity = parse_the_important_things(raw_activity)
            data_db.insert_activity(user_id, activity)
    
    # update database setting variable indicating strava data has been loaded to true
    db = get_db()
    db.execute(
        "UPDATE user SET strava_data = 1 WHERE id = ?",
        (user_id, )
    )
    db.commit()




def is_data_in_db(user_id):
    """ 
    Checks if the Strava data for the given user has already been retrieved
    from Strava and is already loaded into the database.

    Note: this doesn't actually check if the data exists in the database, it 
    just checks a variable associated with the user and saved in a seperate
    database.
    """

    # db = get_db()
    # row = db.execute(
    #     "SELECT * FROM user WHERE id = ?",
    #     (user_id, )
    # ).fetchone()

    # if row["strava_data"] != 0:
    #     return True
    
    return False 


def parse_the_important_things(raw_activity):
    # take a bulky raw activity from Strava and return the important bits

    #TODO: use .get() so things are less fragile...
    return {
        "name": raw_activity["name"],
        "distance": raw_activity["distance"],
        "moving_time": raw_activity["moving_time"],
        "elapsed_time": raw_activity["elapsed_time"],
        "total_elevation_gain": raw_activity["total_elevation_gain"],
        "type": raw_activity["type"],
        "id": raw_activity["id"],
        "start_date": raw_activity["start_date_local"],
        "kudos_count": raw_activity["kudos_count"],
    }

class DataBase():
    """ Wrapper for an sqlite3 database"""

    def __init__(self, filepath="instance/data.sqlite"):
        self._db = sqlite3.connect(filepath)
        self._db.row_factory = sqlite3.Row

        # create DB if it doesn't exist
        self._db.execute(
            "CREATE TABLE IF NOT EXISTS client_data (activity_id INTEGER PRIMARY KEY, client_id INTEGER NOT NULL, activity_type TEXT NOT NULL, activity_date DATE NOT NULL, activity_data TEXT NOT NULL)"
        )

    def insert_activity(self, client_id, data):
        # adds an activity into the client database
        activity_id = data["id"]
        activity_type = data["type"]
        activity_date = data["start_date"].split("T")[0]

        # check that the activity hasn't already been added
        row = self._db.execute(
            "SELECT * FROM client_data WHERE activity_id = ?",
            (activity_id,)
        ).fetchall()

        if row is None:
            self._db.execute(
                "INSERT INTO client_data VALUES (activity_id = ?, client_id = ?, activity_type = ?, activity_date = ?, activity_data = ?)",
                (activity_id, client_id, activity_type, activity_date, data)
            )
            self._db.commit()
    
    def get_activity(self, activity_id):
        # returns the data for a single activity 
        row = self._db.execute(
            "select * from client_data where activity_id = ?",
            (activity_id,)
        ).fetchone()
        return row["activity_data"]

    def get_client_activities(self, client_id):
        # returns a map of all activities for a client
        activities = {}

        for row in self._db.execute("select * from client_data where client_id = ?", (client_id,)):
            activities[row["activity_id"]] = row["activity_data"]

        return activities
