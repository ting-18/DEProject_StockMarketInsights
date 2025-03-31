import os
import logging

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.utils.task_group import TaskGroup
# from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator

from google.cloud import storage
# from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateExternalTableOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
# import pyarrow.csv as pv
# import pyarrow.parquet as pq
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta
import yfinance as yf

PROJECT_ID = 'sylvan-earth-454218-d0'
BUCKET = 'stock_market_storage_bucket'
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", 'stock_market_dataset')

# Load S&P 500 tickers from Wikipedia
SP500_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
TICKERS = pd.read_html(SP500_URL)[0]['Symbol'].tolist()
TICKERS.append("^GSPC")  # append S&P 500 index tikcer
path_to_local_home = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")

def extract_data(tickers, n):
    # Extrat daily stock data for 10 years each ticker from Yahoo Finance API
    if n<10:
        m = (n+1)*50
    else:
        m = len(tickers)
    today = date.today()
    ten_years_ago = today - relativedelta(years=10)
    data = []
    for ticker in tickers[n*50:m]:
        if '.' in ticker:
            ticker = ticker.replace(".", "-")
        stock_data = yf.download(ticker, start=ten_years_ago, end=today, interval="1d")  # Customize as per your need
        data.append(stock_data)

    pdf1 = pd.DataFrame()
    for pdf in data:
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
    pdf1.to_parquet(f"{path_to_local_home}/sp500_stocks_{n}.parquet", index=False)


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


default_args = {
    "owner": "airflow",
    # "start_date": days_ago(1),
    "depends_on_past": False,
    "retries": 1,
}

# Define DAG. This TaskGroup runs around 19 mins.
# NOTE: DAG declaration - using a Context Manager (an implicit way)
with DAG(
    dag_id="stocksdata_gcs_bq_dag",
    # schedule_interval="@daily",
    schedule_interval=None,
    default_args=default_args,
    catchup=False,
    max_active_runs=1,
    tags=['dtc-de'],
) as dag:

    extract_upload_tasks = []
    for n in range((len(TICKERS)//50)+1): 
        with TaskGroup(group_id=f"extract_data_{n}") as task_group1:

            extract_data_task = PythonOperator(
                task_id=f"extract_data_{n}",
                python_callable=extract_data,
                op_kwargs={
                    "tickers": TICKERS,
                    "n": n,
                },
            )            

            local_to_gcs_task = PythonOperator(
                task_id=f"local_to_gcs_{n}",
                python_callable=upload_to_gcs,
                op_kwargs={
                    "bucket": BUCKET,
                    "object_name": f"raw/stocks_data/sp500_stocks_{n}.parquet",
                    "local_file": f"{path_to_local_home}/sp500_stocks_{n}.parquet",
                },
            )

            extract_data_task >> local_to_gcs_task
            # upload_tasks.append(extract_data_task)
            # upload_tasks.append(local_to_gcs_task)        
        extract_upload_tasks.append(task_group1)

    # Task to load CSVs from GCS to BigQuery
    load_parquets_to_bq = GCSToBigQueryOperator(
        task_id=f"load_parquets_to_bq",
        bucket=BUCKET,
        source_objects=["raw/stocks_data/sp500_stocks*.parquet"],
        destination_project_dataset_table=f'{PROJECT_ID}.{BIGQUERY_DATASET}.sp500_stocks_table',
        skip_leading_rows=1,
        source_format='PARQUET',
        write_disposition='WRITE_APPEND', # or WRITE_TRUNCATE to overwrite
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

    # Correct dependencies (Read Graph to check if dependencies are right)
    extract_upload_tasks >> load_parquets_to_bq
    