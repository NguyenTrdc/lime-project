import os
import json
import boto3
from dotenv import load_dotenv
from datetime import datetime, timedelta

import pandas as pd

from google.oauth2 import service_account

from parsing import round_time,string_to_datetime,parse_digits,datetime_to_string

# Load environment variables from .env file
load_dotenv()


def s3_load(bucket_name,topic,ti):
    
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
            
            
        ti.xcom_push(key='df', value = data_day)
        
        print("\n✅ Push to xcom ! ✅\n")

    except Exception as e:
        print("Error:", e)
    
    

def cleaning(task_id,ti):
    try:
        json_object =  ti.xcom_pull(key='df',task_ids=task_id)
        
        # Creating the final DataFrame
        df = pd.DataFrame(json_object)
            
        print("\nDataFrame push into xcom.\n")
            
        # Creating a timestamp id
        df['datetime'] = df['datetime'].apply(lambda input_string: string_to_datetime(input_string))
        df["time_period"] = df["datetime"].apply(lambda x: round_time(x))
        
        df['datetime'] = df['datetime'].apply(lambda input_string: datetime_to_string(input_string))
        df['time_period'] = df['time_period'].apply(lambda input_string: datetime_to_string(input_string))
        
        print(f"\nDATAFRAME SHAPE : {df.shape}\n")
        
        print("\n✅ DataFrame created ! ✅\n")
            
        print(df.head())
        # Convert DataFrame to a JSON object
        json_object = df.to_json(orient='records')
        ti.xcom_push(key='df', value = json_object)
        
        print("\n✅ Push to xcom ! ✅\n")
        
    except Exception as e:
        print("Error:", e)


def uploading_to_BQ(dataset,task_id,ti):
    try:
        # Get the current date and time
        current_datetime = datetime.now()
        yesterday_date = current_datetime - timedelta(days=1)
        
        # Parse the current date and time into separate variables
        year = yesterday_date.year
        month = parse_digits(yesterday_date.month)
        day = parse_digits(yesterday_date.day)
        # Upload df into BigQuery
        table = f"{year}-{month}-{day}"
            
        destination_table = f'{dataset}.{table}'
            
        # Provide the service account credentials
        credentials = service_account.Credentials.from_service_account_file("/opt/airflow/lime-project-key.json")
        
        # Load json from xcom
        json_object =  ti.xcom_pull(key='df',task_ids=task_id)
        json_data = json.loads(json_object)
        
        # Convert it into a DataFrame
        df = pd.DataFrame(json_data)
        
        # Upload it into BigQuery
        df.to_gbq(destination_table=destination_table,project_id='lime-project-394114',if_exists='fail',credentials=credentials)
            
        print(f"\n✅ Table {dataset}/{table} upload on BigQuery! ✅\n")

    except Exception as e:
        print("Error:", e)