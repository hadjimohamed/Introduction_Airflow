from airflow import DAG 
from datetime import datetime,timedelta
from functions import * 
from airflow.operators.python import PythonOperator, BranchPythonOperator 
default_args={
    'owner':'mohamed'
}

with DAG(
    dag_id='branching',
    start_date=datetime(2025,1,21),
    schedule_interval='@once'
) as dag:
    task1=PythonOperator(
        task_id='return_stat_driving_licence',
        python_callable=has_driving
    )
    task2=BranchPythonOperator(
        task_id='verify_driving_licence',
        python_callable=branch
    )
    task3=PythonOperator(
        task_id='can_drive',
        python_callable=eligible_for_driving
    )
    task4=PythonOperator(
        task_id='cant_drive',
        python_callable=note_eligible_for_driving
    )

task1>>task2>>[task3,task4]
