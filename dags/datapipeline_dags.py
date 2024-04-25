# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG
# Operators; we need this to operate!
from airflow.operators.bash import BashOperator
from airflow.utils.dates import datetime
# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'schedule_interval': None}


dag = DAG(
    'scraping_water_comparision',
    default_args=default_args,
    start_date=datetime(2019,1,1),
    catchup=False,
    schedule_interval = None,
    tags=[],
)


t1 = BashOperator(
    task_id='scraping_lotus',
    bash_command='/opt/airflow/miniconda3/envs/bigc/bin/python  /opt/airflow/code/scrape_water_bigc.py',
    dag=dag,
)

t2 = BashOperator(
    task_id='scraping_bigc',
    bash_command='/opt/airflow/miniconda3/envs/bigc/bin/python  /opt/airflow/code/scrape_water_lotus.py',
    dag=dag,
)

t3 = BashOperator(
    task_id='matching_sku',
    bash_command='/opt/airflow/miniconda3/envs/bigc/bin/python  /opt/airflow/code/matching.py',
    dag=dag,
)

t1 >> t3
t2 >> t3