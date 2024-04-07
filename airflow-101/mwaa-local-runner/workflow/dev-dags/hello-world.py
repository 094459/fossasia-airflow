from airflow import DAG
from airflow.utils.dates import days_ago

from airflow.operators.bash import BashOperator

with DAG(
    dag_id="fossasia-hello-world",
    schedule_interval=None,
    catchup=False,
    start_date=days_ago(1)
    ) as dag:

    env_aws_identity = BashOperator(
        task_id="calling_fossasia",
        bash_command="echo FOSSAISA is cool"
    )