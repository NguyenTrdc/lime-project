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


def get_data_velib_metropole():
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
        df["datetime"] = current_date_time

        # #Convert into year, month, day, hour and minute 
        # df["year"] = current_date_time.year
        # df["month"] = current_date_time.month
        # df["day"] = current_date_time.day
        # df["hour"] = current_date_time.hour
        # minute = current_date_time.minute
        # if minute < 30:
        #     df["minute"] = 0
        # else:
        #     df["minute"] = 30
        
        #Dropping every station that is not installed.
        df = df[df['is_installed'] != 0]
        
        #Get the interesting columns.
        df = df[["stationCode","num_bikes_available","numDocksAvailable","datetime"]]
        
        
        return df
        
    except requests.exceptions.RequestException as e:
        print("Error fetching data:", e)


def get_data_opendata():
    api_url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/velib-emplacement-des-stations/records"
    offset = 0
    limit = 100  # Vous pouvez ajuster la limite en fonction de vos besoins
    
    all_results = []
    
    while True:
        params = {
            "offset": offset,
            "limit": limit
        }
    
        response = requests.get(url=api_url, params=params).json()
    
        if "results" not in response:
            break
    
        all_results.extend(response["results"])
    
        if len(response["results"]) < limit:
            break
    
        offset += limit
    
    # Maintenant, all_results contient toutes les stations Velib
    df= pd.DataFrame(all_results)
    df.drop(columns="capacity",inplace=True)
    df.rename(columns={"stationcode": "stationCode"}, inplace=True)

    # Normalize the 'location' column to create separate 'lon' and 'lat' columns
    df[['lon', 'lat']] = pd.json_normalize(df['coordonnees_geo'])
    
            
    # Drop the original 'location' column if needed
    df.drop(columns=['coordonnees_geo'], inplace=True)
    return df


def get_data():
    df1 = get_data_velib_metropole()
    df2 = get_data_opendata()
    merged_df = pd.merge(df1, df2, on="stationCode")
    return merged_df


# Get weather data (in Paris)
def get_Paris_weather():
    # API URL
    api_url = "https://api.open-meteo.com/v1/forecast"
    
    # Parameters
    latitude = 48.866667
    longitude = 2.333333
    hourly_data = "temperature_2m,relativehumidity_2m,precipitation,rain,snowfall,snow_depth,visibility"
    current_weather = "True"
    
    # Query Parameters
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": hourly_data,
        "current_weather": current_weather
    }
    
    try:
        # Make the GET request
        response = requests.get(api_url, params=params)
    
        # Check if the request was successful
        if response.status_code == 200:
            # Convert the response to JSON format
            data = response.json()
            weather_data = {
                "lat": 48.866667,
                "lon": 2.333333,
                "current_weather": data['current_weather'],
                "hourly": {
                    "humidity": data['hourly']['relativehumidity_2m'][0],
                    "precipitation": data['hourly']['precipitation'][0],
                    "rain": data['hourly']['rain'][0],
                    "snowfall": data['hourly']['snowfall'][0],
                    "snow_depth": data['hourly']['snow_depth'][0],
                    "visibility": data['hourly']['visibility'][0]

                }
            }
            # Create a DataFrame from the weather_data dictionary
            current_weather_df = pd.DataFrame.from_dict(weather_data, orient="index").T
            
            # Get the current date and time
            current_date_time = get_current_date_time()
            
            current_weather_df["datetime"] = current_date_time

            #Convert into year, month, day, hour and minute 
            # current_weather_df["year"] = current_date_time.year
            # current_weather_df["month"] = current_date_time.month
            # current_weather_df["day"] = current_date_time.day
            # current_weather_df["hour"] = current_date_time.hour
            # minute = current_date_time.minute
            # if minute < 30:
            #     current_weather_df["minute"] = 0
            # else:
            #     current_weather_df["minute"] = 30
            
            # Normalize the nested dictionaries and merge them into the DataFrame
            current_weather_df = pd.concat([current_weather_df, pd.json_normalize(current_weather_df['current_weather']), pd.json_normalize(current_weather_df['hourly'])], axis=1)
            
            # Drop the original nested dictionary columns
            current_weather_df.drop(columns=['lat','lon','current_weather', 'hourly'], inplace=True)

            current_weather_df = current_weather_df.drop(columns=['time','weathercode'])
            return current_weather_df
    
        else:
            print("Failed to get weather data. Status code:", response.status_code)
    
    except requests.exceptions.RequestException as e:
        print("Error occurred:", e)

print("\nGetting data done ! Starting producing...\n")