# Activity Analysis for Strava

This web app integrates with Strava and allows a user to view their activity data in informative charts.

Currently a user is able to see an overview of their runs or bikerides for any month they were on Strava. 
The chart can be configured to display:
- total moving time 
- total distance
- average pace

# Development
to run the code:
``` 
source startup.sh
flask init-db
flask load-secret
flask run
```

## note: this is a work in progress! Please report any bugs :)
