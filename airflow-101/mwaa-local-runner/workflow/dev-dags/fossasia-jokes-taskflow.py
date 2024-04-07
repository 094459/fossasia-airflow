from airflow.decorators import dag, task
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.amazon.aws.transfers.s3_to_sql import S3ToSqlOperator
from datetime import timedelta, datetime
import requests
import json
import csv
import boto3

@dag(dag_id="nordevcon-funny-jokes-dag", schedule_interval=timedelta(days=1), start_date=datetime(2023, 6, 1), catchup=False, description='The essential collection of bad jokes to keep me amused')

def my_funny_joke_archive_dag():

    # Define some variables - you would typically do this in the Airflow UI
    s3_bucket = "fossasia-airflow-workshop/ricsue"

    time = datetime.now().strftime("%m/%d/%Y").replace('/', '-')
    csv_filename = f"jokes-{time}.csv"
    s3_csv_file= f"{time}/{csv_filename}"

    
    create_joke_table = """
            CREATE TABLE IF NOT EXISTS bad_jokes (
                category TEXT NOT NULL,
                joke TEXT NOT NULL,
                punchline TEXT NOT NULL
            );
        """

    @task
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

    create_joke_table_task = PostgresOperator(
        task_id="create_joke_table",
        sql=create_joke_table,
        postgres_conn_id="postgres-jokes"
        
    )

    csv_generate_task = pull_jokes()

    def parse_csv_to_list(filepath):

        with open(filepath, newline="\n") as file:
            csv_reader = csv.reader(file, delimiter=';')
            next(csv_reader, None)  # Skip the header row
            return list(csv_reader)
        
    SQL_TABLE_NAME = "bad_jokes"
    SQL_COLUMN_LIST = ["category", "joke", "punchline"]

    export_csv_to_postgres = S3ToSqlOperator(
        task_id="export_csv_to_postgres_task",
        s3_bucket=f"{s3_bucket}",
        s3_key=f"{s3_csv_file}",
        table=SQL_TABLE_NAME,
        column_list=SQL_COLUMN_LIST,
        parser=parse_csv_to_list,
        sql_conn_id="postgres-jokes",
    )


    csv_generate_task >> create_joke_table_task >> export_csv_to_postgres

my_funny_joke_archive_dag = my_funny_joke_archive_dag()
