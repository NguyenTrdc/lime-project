from datetime import datetime, timedelta


from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator

from plugins import s3_load,cleaning,uploading_to_BQ

default_args = {
    "owner": "airflow",
    "start_date": datetime(2022, 6, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Loading
def load_stations_data(ti):
    return s3_load('lime-api','lime_stations_topic',ti)

def load_weather_data(ti):
    return s3_load('lime-api','weather_topic',ti)


# Cleaning
def cleaning_stations_data(ti):
    return cleaning("load_stations_data",ti)

def cleaning_weather_data(ti):
    return cleaning("load_weather_data",ti)


# Uploading to BigQUery
def upload_stations_data(ti):
    return uploading_to_BQ("lime_stations_topic","cleaning_stations_data",ti)

def upload_weather_data(ti):
    return uploading_to_BQ("weather_topic","cleaning_weather_data",ti)

        
with DAG(dag_id="S3_to_BigQuery", default_args=default_args, catchup=False, schedule_interval=timedelta(days=1)) as dag:

    load_stations_data = PythonOperator(task_id="load_stations_data", python_callable=load_stations_data,do_xcom_push=False)
    
    load_weather_data = PythonOperator(task_id="load_weather_data", python_callable=load_weather_data,do_xcom_push=False)
    
    
    cleaning_stations_data = PythonOperator(task_id="cleaning_stations_data", python_callable=cleaning_stations_data,do_xcom_push=False)
    
    cleaning_weather_data = PythonOperator(task_id="cleaning_weather_data", python_callable=cleaning_weather_data,do_xcom_push=False)
    
    
    upload_stations_data = PythonOperator(task_id="upload_stations_data", python_callable=upload_stations_data,do_xcom_push=False)
    upload_weather_data = PythonOperator(task_id="upload_weather_data", python_callable=upload_weather_data,do_xcom_push=False)

    join_all = BashOperator(task_id="join_all", bash_command="echo 'Join all!'")

    (   
        [load_stations_data >> cleaning_stations_data >> upload_stations_data,load_weather_data >> cleaning_weather_data >> upload_weather_data]
        >> join_all
    )