# Example written based on the official 
# Confluent Kakfa Get started guide https://github.com/confluentinc/examples/blob/7.1.1-post/clients/cloud/python/consumer.py

from confluent_kafka import Consumer
import json
import ccloud_lib
import time

# Initialize configurations from "python.config" file
CONF = ccloud_lib.read_ccloud_config("python.config")
TOPIC = "lime_API" 

# Create Consumer instance
# 'auto.offset.reset=earliest' to start reading from the beginning of the
# topic if no committed offsets exist
consumer_conf = ccloud_lib.pop_schema_registry_params_from_config(CONF)
consumer_conf['group.id'] = 'lime_consumer'
consumer_conf['auto.offset.reset'] = 'earliest' # This means that you will consume latest messages that your script haven't consumed yet!
consumer = Consumer(consumer_conf)

# Subscribe to topic
consumer.subscribe([TOPIC])

# Process messages
try:
    while True:
        msg = consumer.poll(1.0) # Search for all non-consumed events. It times out after 1 second
        if msg is None:
            # No message available within timeout.
            # Initial message consumption may take up to
            # `session.timeout.ms` for the consumer group to
            # rebalance and start consuming
            print("Waiting for message or event/error in poll()")
            continue
        elif msg.error():
            print('error: {}'.format(msg.error()))
        else:
            # Check for Kafka message
            record_key = msg.key()
            record_value = msg.value()
            data = json.loads(record_value)
            
            n_bikes = data['num_bikes_available']
            timestamp = f"{data['day']}/{data['month']}/{data['year']} {data['hour']}:{data['minute']}"
            print(f"{timestamp} - There was {n_bikes} bikes available at station {data['stationCode']}.")
            time.sleep(1) # Wait a second
except KeyboardInterrupt:
    pass
finally:
    # Leave group and commit final offsets
    consumer.close()