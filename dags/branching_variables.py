from datetime import datetime,timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator 
from functions import *
default_args={
    'owner':'mohamed'
}
with DAG(
    dag_id='branching_variables',
    default_args=default_args,
    start_date=datetime(2025,1,22),
    schedule_interval='@once'
) as dag:
    task1=PythonOperator(
        task_id='read_dataset',
        python_callable=get_data
    )
    task2=PythonOperator(
        task_id='drop_null',
        python_callable=drop_null
    )
    task3=BranchPythonOperator(
        task_id='branch',
        python_callable=branch
    )
    task4=PythonOperator(
        task_id='filter_southwest',
        python_callable=filter_by_southwest
    )
    task5=PythonOperator(
        task_id='filter_southest',
        python_callable=filter_by_southest
    )
    task6=PythonOperator(
        task_id='groupby_smoker_region',
        python_callable=groupby_smoker
    )

task1>>task2>>task3>>[task4,task5,task6]