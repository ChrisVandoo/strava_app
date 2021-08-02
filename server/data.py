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