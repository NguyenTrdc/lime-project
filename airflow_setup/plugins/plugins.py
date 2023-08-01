import os
import json
import boto3
from dotenv import load_dotenv
from datetime import datetime, timedelta

import pandas as pd

from google.oauth2 import service_account

# Load environment variables from .env file
load_dotenv()
    
# Day and Month parser
def parse_digits(n):
    if n<10:
        return '0' + str(n)
    else :
        return str(n)


def s3_to_BQ(bucket_name,topic):
    print("\n heeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeyy \n")
    # Get the current date and time
    current_datetime = datetime.now()
    yesterday_date = current_datetime - timedelta(days=1)
    
    # Parse the current date and time into separate variables
    year = yesterday_date.year
    month = parse_digits(yesterday_date.month)
    day = parse_digits(yesterday_date.day)
    
    prefix = f"topics/{topic}/year={year}/month={month}/day={day}/"
    
    s3 = boto3.client('s3', aws_access_key_id= os.getenv("AWS_ACCESS_KEY_ID"), aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"))
    data_day = []
    
    try:
        # List all objects with the given prefix
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        
        for obj in response.get('Contents', []):
            # Get the object key (file path)
            file_key = obj['Key']

            # Retrieve the object content
            response = s3.get_object(Bucket=bucket_name, Key=file_key)
            
            data = response['Body'].read().decode('utf-8')
            
            # Split the input string into individual JSON objects based on newline character
            json_objects = data.strip().split('\n')
            
            # Parse each JSON object into a dictionary
            parsed_data = [json.loads(obj) for obj in json_objects]

            data_day += parsed_data
        df = pd.DataFrame(data_day)
        print("\n✅ DataFrame created ! ✅\n")
        # Upload df into BigQuery
        table = f"{year}-{month}-{day}"
        
        destination_table = f'{topic}.{table}'
        
        # Provide the service account credentials
        credentials = service_account.Credentials.from_service_account_file("/opt/airflow/pluginslime-project-key.json")
        
        df.to_gbq(destination_table=destination_table,project_id='lime-project-394114',if_exists='fail',credentials=credentials)
        
        print(f"\n✅ Table {table} upload on BigQuery! ✅\n")

    except Exception as e:
        print("Error:", e)
        
