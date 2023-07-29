import requests
import pandas as pd
import json

from datetime import datetime
import pytz

def get_current_date_time():
    # Get the current time in the UTC timezone
    utc_now = datetime.now(pytz.utc)

    # Convert the UTC time to the Paris timezone
    paris_tz = pytz.timezone('Europe/Paris')
    paris_now = utc_now.astimezone(paris_tz)

    return paris_now


def get_data():
    url = "https://velib-metropole-opendata.smoove.pro/opendata/Velib_Metropole/station_status.json"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for any errors in the response

        # If the request was successful, parse the JSON data
        data = response.json()

        # Extract the 'stations' list from the JSON data
        stations_data = data["data"]["stations"]

        # Create a DataFrame from the 'stations' list
        df = pd.DataFrame(stations_data)

        # Get the current date and time
        current_date_time = get_current_date_time()

        #Convert into year, month, day, hour and minute 
        df["year"] = current_date_time.year
        df["month"] = current_date_time.month
        df["day"] = current_date_time.day
        df["hour"] = current_date_time.hour
        df["minute"] = current_date_time.minute
        
        #Dropping every station that is not installed.
        df = df[df['is_installed'] != 0]
        
        #Get the interesting columns.
        df = df[["stationCode","num_bikes_available","numDocksAvailable","year","month","day","hour","minute"]]
        
        return df
        
    except requests.exceptions.RequestException as e:
        print("Error fetching data:", e)
    