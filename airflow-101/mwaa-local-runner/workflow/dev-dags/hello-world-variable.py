from airflow import DAG
from airflow.utils.dates import days_ago

from airflow.operators.bash import BashOperator

# add airflow import to work with variables

from airflow.models import Variable

# define our variable

demovariable = Variable.get("event", default_var="undefined")
print(demovariable)

with DAG(
    dag_id="fossasia-hello-world-variable",
    schedule_interval=None,
    catchup=False,
    start_date=days_ago(1)
    ) as dag:

    env_aws_identity = BashOperator(
        task_id="calling_fossasia",
        #bash_command='echo "{{ var.value.event }}"'
        bash_command='echo "{demovariable}"'.format(demovariable=demovariable)
    )