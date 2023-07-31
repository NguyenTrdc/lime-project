# Code inspired from Confluent Cloud official examples library
# https://github.com/confluentinc/examples/blob/7.1.1-post/clients/cloud/python/producer.py

from confluent_kafka import Producer
import json
import ccloud_lib # Library not installed with pip but imported from ccloud_lib.py
import time

from get_data import get_data, get_Paris_weather

# Initialize configurations from "python.config" file
CONF = ccloud_lib.read_ccloud_config("python.config")
TOPIC_stations = "real_time_lime_API"
TOPIC_weather = "real_time_weather"

# Create Producer instance
producer_conf = ccloud_lib.pop_schema_registry_params_from_config(CONF)
producer_stations = Producer(producer_conf)
producer_weather = Producer(producer_conf)
# Create topic if it doesn't already exist
ccloud_lib.create_topic(CONF, TOPIC_stations)
ccloud_lib.create_topic(CONF, TOPIC_weather)

try:
    # Starts an infinite while loop that produces records from the DataFrame
    
    while True:
        
        # Get stations data
        result_stations = get_data()
        
        # Get weather data
        ressult_weather = get_Paris_weather()
        
        print("\n⌛ Producing... ⌛\n")
        
                    
        for index, row in ressult_weather.iterrows():
            record_value_weather = json.dumps(
                {
                    "year": int(row["year"]),
                    "month": int(row["month"]),
                    "day": int(row["day"]),
                    "hour": int(row["hour"]),
                    "minute": int(row["minute"]),
                    "temperature": float(row["temperature"]),
                    "windspeed": float(row["windspeed"]),
                    "is_day": int(row["is_day"]),
                    "humidity": float(row["humidity"]),
                    "precipitation": float(row["precipitation"]),
                    "rain": float(row["rain"]),
                    "snowfall": float(row["snowfall"]),
                    "snow_depth": float(row["snow_depth"]),
                    "visibility": float(row["visibility"]),
                    
                }
            )
            producer_weather.produce(
                TOPIC_weather,
                key="Paris_weather",
                value=record_value_weather,
            )
            producer_weather.flush()  # Flush to ensure the record is sent immediately

            print("\nProducing record weather {}\t{}\n".format("Paris weather", record_value_weather))
            
        # Producing stations data
        size = len(result_stations)
        
        for index, row in result_stations.iterrows():
            record_key = str(row["stationCode"])

            record_value_station = json.dumps(
                {
                    "stationCode": int(row["stationCode"]),
                    "num_bikes_available": int(row["num_bikes_available"]),
                    "numDocksAvailable": int(row["numDocksAvailable"]),
                    "year": int(row["year"]),
                    "month": int(row["month"]),
                    "day": int(row["day"]),
                    "hour": int(row["hour"]),
                    "minute": int(row["minute"]),
                    "name": str(row["name"]),
                    "lat": float(row["lat"]),
                    "lon": float(row["lon"])
                }
            )
            
            # This will actually send data to your topic
            producer_stations.produce(
                TOPIC_stations,
                key=record_key,
                value=record_value_station,
            )
            producer_stations.flush()  # Flush to ensure the record is sent immediately
            #print("Producing record station: {}\t{}".format(record_key, record_value_station),end="",flush=True)
            print(f"Producing stations data : {index}/{size} done.",end="", flush=True)
            # Clear the last printed line using '\r'
            print("\r", end="", flush=True)
            
        print("Producing record station: {}\t{}".format(record_key, record_value_station),end="",flush=True)
        print("\n✅ Producing data done ! ✅\n")
        time.sleep(60) # Wait an hour before producing new data


# Interrupt infinite loop when hitting CTRL+C
except KeyboardInterrupt:
    pass
finally:
    producer_weather.flush()  # Finish producing the latest event before stopping the whole script
    producer_stations.flush() 