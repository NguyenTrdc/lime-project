# Code inspired from Confluent Cloud official examples library
# https://github.com/confluentinc/examples/blob/7.1.1-post/clients/cloud/python/producer.py

from confluent_kafka import Producer
import json
import ccloud_lib # Library not installed with pip but imported from ccloud_lib.py
import time

from get_data import get_data

# Initialize configurations from "python.config" file
CONF = ccloud_lib.read_ccloud_config("python.config")
TOPIC = "lime_API" 

# Create Producer instance
producer_conf = ccloud_lib.pop_schema_registry_params_from_config(CONF)
producer = Producer(producer_conf)

# Create topic if it doesn't already exist
ccloud_lib.create_topic(CONF, TOPIC)


try:
    # Starts an infinite while loop that produces records from the DataFrame
    
    df = get_data()
    
    while True:
        for index, row in df.iterrows():
            record_key = str(row["stationCode"])
            record_value = json.dumps(
                {
                    "stationCode": int(row["stationCode"]),
                    "num_bikes_available": int(row["num_bikes_available"]),
                    "numDocksAvailable": int(row["numDocksAvailable"]),
                    "year": int(row["year"]),
                    "month": int(row["month"]),
                    "day": int(row["day"]),
                    "hour": int(row["hour"]),
                    "minute": int(row["minute"]),
                }
            )
            print("Producing record: {}\t{}".format(record_key, record_value))

            # This will actually send data to your topic
            producer.produce(
                TOPIC,
                key=record_key,
                value=record_value,
            )
            producer.flush()  # Flush to ensure the record is sent immediately
            
        time.sleep(3600) # Wait an hour before producing new data


# Interrupt infinite loop when hitting CTRL+C
except KeyboardInterrupt:
    pass
finally:
    producer.flush()  # Finish producing the latest event before stopping the whole script