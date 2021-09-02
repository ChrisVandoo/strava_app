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
import json
from datetime import datetime 
from dateutil.parser import isoparse
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
    
    data_db.shutdown()

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
            "CREATE TABLE IF NOT EXISTS client_data (activity_id INTEGER NOT NULL, client_id INTEGER NOT NULL, activity_type TEXT NOT NULL, activity_date DATETIME NOT NULL, activity_data TEXT NOT NULL);"
        )
        if self._db.in_transaction:
            print("committing the DB")
            self._db.commit()

    def shutdown(self):
        self._db.close()

    def insert_activity(self, client_id, data):
        # adds an activity into the client database
        activity_id = data["id"]
        activity_type = data["type"]
        activity_date = isoparse(data["start_date"])

        # check that the activity hasn't already been added
        row = self._db.execute(
            "SELECT * FROM client_data WHERE activity_id = ?",
            (activity_id,)
        ).fetchall()

        if row == []:
            print("inserting {}".format(data))
            self._db.execute(
                "INSERT INTO client_data (activity_id, client_id, activity_type, activity_date, activity_data) VALUES (?, ?, ?, ?, ?);",
                (activity_id, client_id, activity_type, activity_date, json.dumps(data))
            )
            self._db.commit()
        else:
            print("Activity already exists in the DB, not adding it! activity_id: {}".format(activity_id))
    
    def get_activity(self, activity_id):
        # returns the data for a single activity 
        row = self._db.execute(
            "select * from client_data where activity_id = ?",
            (activity_id,)
        ).fetchone()

        if row is not None:
            return row["activity_data"]
        
        return None

    def get_oldest_activity(self, client_id):
        """
        Find the oldest activity for a given athlete.
        """

        # this should order all activities with the oldest activity first 
        row = self._db.execute(
            "SELECT * FROM client_data ORDER BY activity_date"
        ).fetchone()

        if row is not None:
            return row["activity_date"]

        return None


    def get_client_activities(self, client_id, type="All", after=None, before=None):
        """
        Returns the activities for a given athlete, specified by client_id.

        Optional Parameters:
        date: return all activities after a given date -> the present
        type: return all activities of a given type
        """

        query = "client_id=:id"
        args = {"id": client_id}

        if after is not None and before is not None:
            if isinstance(after, datetime) and isinstance(before, datetime):
                query+=" AND activity_date>=:after"
                args["after"] = after

                query+=" AND activity_date<=:before"
                args["before"] = before
        
        if type != "All":
            if type == "Ride" or type == "Run":
                # type MUST be Ride or Run or else we ignore type
                query+=" AND activity_type=:type"
                args["type"] = type 

        activities = {}

        # print(query, args)

        for row in self._db.execute("select * from client_data where ({})".format(query), args):
            activities[isoparse(row["activity_date"])] = row["activity_data"]

        #print(activities)
        return activities
