import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Day and Month parser
def parse_digits(n):
    if n<10:
        return '0' + str(n)
    else :
        return str(n)

def round_time(dt):
    # Round to the nearest 30 minutes
    round_to = 30
    minutes = dt.minute
    if minutes < round_to:
        minutes = 0
    else:
        minutes = round_to

    dt = dt.replace(second=0, microsecond=0, minute=0, hour=dt.hour)
    dt += timedelta(minutes=minutes)
    return dt


def string_to_datetime(input_string):
    # Format to parse the input string
    format_string = "%Y-%m-%d %H:%M:%S.%f%z"
    
    # Convert the string to a datetime object
    datetime_object = datetime.strptime(input_string, format_string)
    
    return datetime_object


def datetime_to_string(datetime):
    # Convert datetime to string with a specific format
    date_string = datetime.strftime('%Y-%m-%d %H:%M:%S')
    
    return date_string