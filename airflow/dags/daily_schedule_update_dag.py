import os
import logging

from airflow import DAG
from airflow.utils.dates import days_ago
# from airflow.utils.task_group import TaskGroup
from airflow.models import Variable
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
# from airflow.providers.postgres.operators.postgres import PostgresOperator

from google.cloud import storage
from google.cloud import bigquery
# from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateExternalTableOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
# import pyarrow.csv as pv
# import pyarrow.parquet as pq
import pandas as pd
# from datetime import date
# from dateutil.relativedelta import relativedelta
import yfinance as yf


#TODO：Replace with your own PROJECT_ID,BUCKET, DATESET
PROJECT_ID = 'sylvan-earth-454218-d0'
BUCKET = 'stock_market_storage_bucket'
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", 'stock_market_dataset')

# Load S&P 500 tickers from Wikipedia
SP500_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
TICKERS = pd.read_html(SP500_URL)[0]['Symbol'].tolist()
TICKERS.append("^GSPC")  # append S&P 500 index tikcer
path_to_local_home = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")



def get_last_processed_date():
    """Retrieve the last processed date from Airflow Variables."""
    return Variable.get("last_date", default_var="2025-03-25")

def update_last_processed_date(new_date):
    """Update the last processed date in Airflow Variables."""
    Variable.set("last_date", new_date)

last_date = get_last_processed_date()

def extract_new_data(tickers, last_date):
    # Extrat new daily stock data for each ticker from Yahoo Finance API
    # last_date = get_last_processed_date()
    new_data = []
    for ticker in tickers:
        if '.' in ticker:
            ticker = ticker.replace(".", "-")
        stock_data = yf.download(ticker, start=last_date, interval="1d")  # Customize as per your need
        if stock_data.empty:
            print("No new data to extract.")
            return None
        new_data.append(stock_data)
    pdf1 = pd.DataFrame()
    for pdf in new_data:
        pdf['Ticker'] = pdf.columns[0][1]
        pdf.columns = pdf.columns.droplevel('Ticker')
        pdf.columns.name =None
        pdf= pdf.reset_index()
        # Convert datetime64 to pure DATE type Instead of TIMESTAMP
        pdf["Date"] = pdf["Date"].dt.date
        # # Or convert datetime64 to string
        # df["Date"] = pdf["Date"].astype(str)
        # As some parquet will store 'Volume' as int64, some as float
        # Check if 'Volume' is stored as float and Round,convert to int
        if pdf["Volume"].dtype == "float64":            
            pdf["Volume"] = pdf["Volume"].round().astype("int64")
        pdf=pdf.round(4)
        pdf2 =pdf.loc[:, ["Date","Ticker", "Open","Close","High","Low","Volume"]]
        pdf1= pd.concat([pdf1, pdf2])
    pdf1.to_parquet(f"{path_to_local_home}/new_data.parquet", index=False)
    if pdf1 is not None:
        new_last_date = pdf1["Date"].max()
        update_last_processed_date(new_last_date)


def upload_to_gcs(bucket, object_name, local_file):
    # When upload_to_gcs, storage.Client() got Project_ID from Service_Account_Credential_Key.json
    # (i.e.docker_compose.yaml: GOOGLE_APPLICATION_CREDENTIALS: /.google/credentials/google_credentials.json)
    """
    Ref: https://cloud.google.com/storage/docs/uploading-objects#storage-upload-object-python
    :param bucket: GCS bucket name
    :param object_name: target path & file-name
    :param local_file: source path & file-name
    :return:
    """
    # WORKAROUND to prevent timeout for files > 6 MB on 800 kbps upload speed.
    # (Ref: https://github.com/googleapis/python-storage/issues/74)
    storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024  # 5 MB
    storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024  # 5 MB
    # End of Workaround

    client = storage.Client()
    bucket = client.bucket(bucket)

    blob = bucket.blob(object_name)
    blob.upload_from_filename(local_file)


def merge_into_bigquery(dataset_id, target_table, staging_table):
    """Merge data from staging table into the main BigQuery table (UPSERT)."""
    client = bigquery.Client()
    query = f"""
    MERGE `{dataset_id}.{target_table}` AS target
    USING `{dataset_id}.{staging_table}` AS source
    ON target.Ticker = source.Ticker AND target.Date = source.Date
    WHEN MATCHED THEN 
        UPDATE SET 
            target.Open = source.Open,
            target.High = source.High,
            target.Low = source.Low,
            target.Close = source.Close,
            target.Volume = source.Volume
    WHEN NOT MATCHED THEN 
        INSERT (Date, Ticker, Open, High, Low, Close, Volume)
        VALUES (source.Date, source.Ticker, source.Open, source.High, source.Low, source.Close, source.Volume);
    """

    query_job = client.query(query)
    query_job.result()  # Wait for the job to complete

    print(f"Merged staging table into {dataset_id}.{target_table}")




default_args = {
    "owner": "airflow",
    "start_date": days_ago(1),
    "depends_on_past": False,
    "retries": 1,
}

# Define DAG. This TaskGroup runs around 19 mins.
# NOTE: DAG declaration - using a Context Manager (an implicit way)
with DAG(
    dag_id="newdata_gcs_bq_dbt_dag",
    schedule_interval="@daily",
    # schedule_interval=None,
    default_args=default_args,
    catchup=False,
    max_active_runs=1,
    tags=['dtc-de'],
) as dag:
   
    extract_new_data_task = PythonOperator(
        task_id=f"extract_new_data",
        python_callable=extract_new_data,
        op_kwargs={
            "tickers": TICKERS, 
            "last_date": last_date,                   
        },
    )            

    local_to_gcs_task = PythonOperator(
        task_id=f"local_to_gcs",
        python_callable=upload_to_gcs,
        op_kwargs={
            "bucket": BUCKET,
            "object_name": f"raw/stocks_data/new_data.parquet",
            "local_file": f"{path_to_local_home}/new_data.parquet",
        },
    )

    # Task to load parquet from GCS to BigQuery staging table
    load_parquets_to_bq_staging = GCSToBigQueryOperator(
        task_id=f"load_parquets_to_bq_staging",
        bucket=BUCKET,
        source_objects=["raw/stocks_data/new_data.parquet"],
        destination_project_dataset_table=f'{PROJECT_ID}.{BIGQUERY_DATASET}.staging_data_table',
        skip_leading_rows=1,
        source_format='PARQUET',
        write_disposition='WRITE_TRUNCATE', # or WRITE_TRUNCATE to overwrite
        field_delimiter=",",
        schema_fields=[
            {"name": "Date", "type": "DATE", "mode": "NULLABLE"},
            {"name": "Close", "type": "FLOAT64", "mode": "NULLABLE"},
            {"name": "High", "type": "FLOAT64", "mode": "NULLABLE"},
            {"name": "Low", "type": "FLOAT64", "mode": "NULLABLE"},
            {"name": "Open", "type": "FLOAT64", "mode": "NULLABLE"},
            {"name": "Volume", "type": "INTEGER", "mode": "NULLABLE"},
            {"name": "Ticker", "type": "STRING", "mode": "NULLABLE"},
        ],
        autodetect=False,  # Disable autodetect to enforce schema
    )

    # Task to update existing records and insert new ones.
    merge_task = PythonOperator(
        task_id="merge_into_bigquery",
        python_callable=merge_into_bigquery,  
        op_kwargs={
            "dataset_id": BIGQUERY_DATASET, 
            "target_table": f"sp500_stocks_table", 
            "staging_table": f"staging_data_table",
        },      
    )

    # Task to run a dbt project 
    dbt_run_task = BashOperator(
        task_id="dbt_run_task",
        # bash_command= "cd /opt/airflow/dbt && dbt run --profiles-dir /opt/airflow/dbt",
        bash_command="cd /opt/airflow/dbt && dbt build",
    )

    # Correct dependencies (Read Graph to check if dependencies are right)
    extract_new_data_task >> local_to_gcs_task >> load_parquets_to_bq_staging >> merge_task >> dbt_run_task




