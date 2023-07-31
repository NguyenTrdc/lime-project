#!/bin/bash

# Run consumer_stations.py in the background
python consumer_stations.py &

# Run consumer_weather.py in the background
python consumer_weather.py &

# Add any additional commands or configurations here, if needed

# Wait for both scripts to finish
wait