#!/bin/bash

# Run Producer
echo "Running Producer and Consumer..."

# Run the producer script in the background
python3 producer.py &

# Run the consumer script in the background
python3 consumer.py &

echo "Producer and Consumer are running !"

# Wait for both scripts to finish
wait