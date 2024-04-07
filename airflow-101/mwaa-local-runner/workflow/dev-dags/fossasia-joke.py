from airflow import DAG
from datetime import datetime
from airflow.utils.dates import days_ago

import requests
import json
import csv
import boto3

from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.amazon.aws.transfers.s3_to_sql import S3ToSqlOperator
from airflow.operators.python import PythonOperator

s3_bucket="fossasia-apache-airflow-workshop"
unique_name="7818123444"
time = datetime.now().strftime("%m/%d/%Y").replace('/', '-')
csv_filename = f"jokes-{time}.csv"
s3_csv_file= f"{unique_name}/{time}/{csv_filename}"

with DAG(
    dag_id="fossasia-joke",
    schedule_interval='* 2 * * *',
    catchup=False,
    start_date=days_ago(1)
    ) as dag:

    create_joke_table = """
            CREATE TABLE IF NOT EXISTS bad_jokes (
                category TEXT NOT NULL,
                joke TEXT NOT NULL,
                punchline TEXT NOT NULL
            );
        """
    create_joke_table_task = PostgresOperator(
        task_id="create_joke_table",
        sql=create_joke_table,
        postgres_conn_id="postgres-jokes"
        
    )


    def pull_jokes():
                # pull jokes with the API
        url = r"https://official-joke-api.appspot.com/random_ten"
        response = requests.get(url)
        text = json.loads(response.text)

        # export to csv
        with open(csv_filename, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=';')
            csv_writer.writerow(['Type', 'Setup', 'Punchline'])
            for i in text:
                csv_writer.writerow([i['type'], i['setup'], i['punchline']])
                print(i)

        # strip quotes
        with open(csv_filename, "r+", encoding="utf-8") as csv_file:
            content = csv_file.read()
        with open(csv_filename, "w+", encoding="utf-8") as csv_file:
            csv_file.write(content.replace('"', ''))

        # upload data_file to S3 bucket
        s3_client = boto3.client('s3')
        s3_client.upload_file(csv_filename, s3_bucket, s3_csv_file)
        print(f"File {csv_filename} uploaded to S3 bucket {s3_bucket}")
        
        return None
    
    download_jokes = PythonOperator(
        task_id='grab_jokes',
        python_callable=pull_jokes)
    

    def parse_csv_to_list(filepath):
        with open(filepath, newline="\n") as file:
            csv_reader = csv.reader(file, delimiter=';')
            next(csv_reader, None)  # Skip the header row
            return list(csv_reader)
        
    def parse_csv_to_list_modified(filepath):
        with open(filepath, newline="\n") as file:
            csv_reader = csv.reader(file, delimiter=';')
            next(csv_reader, None)  # Skip the header row
            rows = []
            for row in csv_reader:
                if row[0] == "knock-knock":
                    return []  # Return an empty list if "knock-knock" is found
                rows.append(row)
            return rows
        
    SQL_TABLE_NAME = "bad_jokes"
    SQL_COLUMN_LIST = ["category", "joke", "punchline"]

    export_jokes_to_postgres = S3ToSqlOperator(
        task_id="export_csv_to_postgres_task",
        s3_bucket=f"{s3_bucket}",
        s3_key=f"{s3_csv_file}",
        table=SQL_TABLE_NAME,
        column_list=SQL_COLUMN_LIST,
        parser=parse_csv_to_list_modified,
        sql_conn_id="postgres-jokes",
    )


    create_joke_table_task >> download_jokes >> export_jokes_to_postgres

