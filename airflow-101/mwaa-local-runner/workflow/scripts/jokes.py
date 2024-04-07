import requests
import json
from datetime import datetime
import csv
import boto3

s3_bucket="fossasia-apache-airflow-workshop"
unique_name="7818123444"

time = datetime.now().strftime("%m/%d/%Y").replace('/', '-')
csv_filename = f"jokes-{time}.csv"
s3_csv_file= f"{unique_name}/{time}/{csv_filename}"

def pull_jokes():

    # pull jokes with the api
    url = r"https://official-joke-api.appspot.com/random_ten"
    response = requests.get(url)
    text = json.loads(response.text)
   

    # export to csv

    csv_file = open(csv_filename, 'w')
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['Type', 'Setup', 'Punchline'])
    for i in text:
        csv_writer.writerow([i['type'], i['setup'], i['punchline']])
        print(i)
    csv_file.close()

    # strip quotes

    with open(csv_filename, "r+", encoding="utf-8") as csv_file:
        content = csv_file.read()
    with open(csv_filename, "w+", encoding="utf-8") as csv_file:
        csv_file.write(content.replace('"', ''))

    # upload data_file to s3 bucket

    s3_client = boto3.client('s3')
    s3_client.upload_file(csv_filename, s3_bucket, s3_csv_file)
    print(f"File {csv_filename} uploaded to s3 bucket {s3_bucket}")

pull_jokes()