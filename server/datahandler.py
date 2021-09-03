"""
DataHandler - class to manipulate and parse Strava data.

- should return data for a specific time range:
    - this shouldn't actually require a date, just 1 week from "current" -> 1 year from "current"
- should be able to specify activity type, initially this will be limited to Run or Ride
- should return data ready to be used by Chart.js -> probably a dict of (pace|distance|time):(date)

"""


from dateutil.parser import isoparse
from calendar import Calendar
from datetime import date, datetime, time 
from server.data import DataBase
import json
from math import floor

def get_last_day_of_month(year, month):
    # given a year and month, returns the last day of the month
    last_day = 0
    for day in Calendar().itermonthdays(year, month):
        if day != 0:
            last_day = day
    return last_day

def go_to_last_month():
    now = datetime.now()

    if now.month == 1:
        return now.replace(year=now.year-1, month=12)
    else:
        return now.replace(month=now.month-1)

def get_pace(activity, activity_type):
    """
    return seconds/km if activity_type is Run
    return km/hour if activity_type is Bike 
    """
    distance = round(activity.get("distance", 0) / 1000, 2)

    if activity_type == "Run":
        # pace in seconds/km
        pace_in_seconds = round(activity.get("moving_time", 1) / distance, 3)
        return pace_in_seconds
    else:
        total_time = round(activity.get("moving_time", 0) / 3600, 2)
        pace = round(distance / total_time, 2)
        return pace

def format_run_pace(pace_in_seconds):
    # nicely format pace for runs min:sec
    pace_in_min = pace_in_seconds / 60
    minutes = floor(pace_in_min)
    seconds = round((pace_in_min % minutes) * 60)

    if seconds / 10 >= 1:
        return "Average Pace: {}:{} /km".format(minutes, seconds)
    else:
        return "Average Pace: {}:0{} /km".format(minutes, seconds)

def format_time(total_time):
    # takes a time in minutes and converts it to HH:MM
    if total_time < 60:
        return "{}m".format(total_time)

    in_hours = total_time / 60
    hours = floor(total_time / 60)
    minutes = round((in_hours % hours) * 60)
 
    return "{}h {}m".format(hours, minutes)


class DataHandler():
    """ Return data in a way convenient to be displayed by Chart.js """

    def __init__(self, user_id):
        self._db = DataBase()
        self._user_id = user_id

    def get_some_activities(self):
        print ("Activity dump ")
        stuff = self._db.get_client_activities(self._user_id)
        print(stuff)

        # print("Get a single activity...")
        # stuff = self._db.get_activity(5623218522)
        # print(stuff)

        # print("Retrieving rides")
        # stuff = self._db.get_client_activities(self._user_id, "Ride")
        # print(stuff)

        # print("Retrieiving runs that were run this month")
        # the_date = datetime(2021, 8, 1, 0, 0, 0)
        # print(the_date)
        # stuff = self._db.get_client_activities(self._user_id, "Run", the_date)
        # print(stuff)

        # stuff = self._db.get_oldest_activity(self._user_id)
        # print(stuff)

    def get_years_on_strava(self):
        """
        returns an array of integers listing the years the user has been on Strava
        """
        oldest_activity = isoparse(self._db.get_oldest_activity(self._user_id))

        year = datetime.now().year
        years = []
        while year >= oldest_activity.year:
            years.append(year)
            year-=1

        return years

    def get_totals_for_month(self, month, year, activity_type="All"):
        """
        Return the total distance moved, time spent moving, and the average 
        pace for the month.
        """

        data = self._db.get_client_activities(self._user_id, activity_type, datetime(year, month, 1), datetime(year, month, get_last_day_of_month(year, month)))
        if data == {}:
            print("didn't find any data within the last month :(")
            return {}

        monthly_totals = {
            "total_distance": 0,
            "total_time": 0,
            "avg_pace": 0
        }

        pace = []

        for _, activity_str in data.items():
            activity = json.loads(activity_str)

            # distance in km
            monthly_totals["total_distance"] += round(activity.get("distance") / 1000, 2)
            # time in minutes
            monthly_totals["total_time"] += round(activity.get("elapsed_time") / 60)
            
            pace.append(get_pace(activity, activity_type))

        monthly_totals["total_distance"] = round(monthly_totals["total_distance"], 1)            
        monthly_totals["total_time"] = format_time(monthly_totals["total_time"])

        if activity_type == "Run":
            monthly_totals["avg_pace"] = format_run_pace(round(sum(pace) / len(pace), 2))
        else:
            monthly_totals["avg_pace"] = "Average Speed: {} km/h".format(round(sum(pace) / len(pace), 2)) 

        return monthly_totals

    def get_runs_for_month(self, month, year, activity_type="All", rep_type="distance"):
        """
        month: integer specifiying which month to get data for, defaults to January (1)
        year: integer specifying the year, if it is None, defaults to the current year
        """

        
        chart_data = {}

        last_day = 0
        for day in Calendar().itermonthdays(year, month):
            if day != 0:
                last_day = day

                # the graph will get weird if all the days are filled in for pace
                if rep_type != "pace":
                    chart_data[date(year, month, day).isoformat()] = 0

        data = self._db.get_client_activities(self._user_id, activity_type, datetime(year, month, 1), datetime(year, month, last_day))
        if data == {}:
            print("didn't find any data within the last month :(")
            return {}
        
        # iterate through activities for the month, getting the y-axis value (pace, distance, time)
        for my_date, activity_str in data.items():
            activity = json.loads(activity_str)
            
            if rep_type == "distance":
                y = round(activity.get("distance") / 1000, 2)
            elif rep_type == "time":
                y = round(activity.get("elapsed_time") / 60, 0)
            elif rep_type == "pace":
                y = get_pace(activity, activity_type)

            chart_data[my_date.date().isoformat()] = y

        
        return chart_data


        