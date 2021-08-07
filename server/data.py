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

def parse_the_important_things(raw_activity):
    # take a bulky raw activity from Strava and return the important bits
    return {
        "name": raw_activity["name"],
        "distance": raw_activity["distance"],
        "moving_time": raw_activity["moving_time"],
        "elapsed_time": raw_activity["elapsed_time"],
        "total_elevation_gain": raw_activity["total_elevation_gain"],
        "type": raw_activity["type"],
        "id": raw_activity["id"],
        "start_date": raw_activity["start_date"],
        "kudos_count": raw_activity["kudos_count"],
    }

class DataBase():
    """ Wrapper for an sqlite3 database"""

    def __init__(self, filepath="instance/data.sqlite"):
        self._db = sqlite3.connect(filepath)
        self._db.row_factory = sqlite3.Row

        # create DB if it doesn't exist
        self._db.execute(
            "CREATE TABLE IF NOT EXISTS client_data (activity_id INTEGER PRIMARY KEY, client_id INTEGER NOT NULL, activity_data TEXT NOT NULL)"
        )

    def insert_activity(self, activity_id, client_id, data):
        # adds an activity into the client database

        # check that the activity hasn't already been added
        row = self._db.execute(
            "SELECT * FROM client_data WHERE activity_id = ?",
            (activity_id,)
        ).fetchall()

        if row is None:
            self._db.execute(
                "INSERT INTO client_data VALUES (activity_id = ?, client_id = ?, activity_id = ?)",
                (activity_id, client_id, data, activity_id)
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
