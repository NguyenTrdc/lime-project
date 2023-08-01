from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator

from plugins import s3_to_BQ


default_args = {
    "owner": "airflow",
    "start_date": datetime(2022, 6, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


def upload_stations_to_bq():
    return s3_to_BQ('lime-api','lime_stations_topic')


def upload_weather_to_bq():
    return s3_to_BQ('lime-api','weather_topic')



        
with DAG(dag_id="s3_to_BigQuery", default_args=default_args, catchup=False, schedule_interval=timedelta(days=1)) as dag:

    upload_stations_to_bq = PythonOperator(task_id="stations_data_to_BQ", python_callable=upload_stations_to_bq)
    
    upload_weather_to_bq = PythonOperator(task_id="weather_data_to_BQ", python_callable=upload_weather_to_bq)

    join_all = BashOperator(task_id="join_all", bash_command="echo 'Join all!'")

    (   
        [upload_stations_to_bq,upload_weather_to_bq]
        >> join_all
    )