import pandas as pd

from google.oauth2 import service_account
from google.cloud import bigquery

def get_all_data_from_BQ(dataset_id):
    
    # Get crendentials
    credentials = service_account.Credentials.from_service_account_file("/home/andre/Downloads/lime-key.json")

    # Create a BigQuery client
    client = bigquery.Client(credentials=credentials)
    
    # Specify the project ID
    project_id = "lime-project-394114"
    
    # List the tables in the dataset
    tables = client.list_tables(f"{project_id}.{dataset_id}")
    
    # Initialize an empty list to store table data
    table_data_list = []
    
    # Iterate through the tables and fetch data
    for table in tables:
        table_ref = client.dataset(dataset_id).table(table.table_id)
        table_data = client.list_rows(table_ref).to_dataframe()
        table_data_list.append(table_data)
    
    # Concatenate all table data into a single DataFrame
    concatenated_df = pd.concat(table_data_list, ignore_index=True)
    
    # Print the first few rows of the concatenated DataFrame
    return concatenated_df
