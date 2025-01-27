from datetime import datetime,timedelta 
from airflow import DAG 
from airflow.operators.python import PythonOperator, BranchPythonOperator 
from functions import *
from airflow.utils.task_group import TaskGroup
from airflow.utils.edgemodifier import Label
default_args={
    'owner':'mohamed'
}
with DAG(
    dag_id='taskgroupbs_edgelabels',
    default_args=default_args,
    start_date=datetime(2025,1,22),
    schedule_interval='@once'
) as dag:
    
    with TaskGroup('reading_data_processisng_data') as reading_data_processisng_data:
        task1=PythonOperator(
            task_id='read_dataset',
            python_callable=get_my_data
        )
        task2=PythonOperator(
            task_id='drop_null',
            python_callable=null_values
        )
        task1>>task2

    task3=BranchPythonOperator(
        task_id='branch',
        python_callable=my_branch
    )

    with TaskGroup('filtering') as filtering:
        task4=PythonOperator(
            task_id='filter_by_southwest',
            python_callable=by_southwest
        )
        task5=PythonOperator(
            task_id='filter_by_southeast',
            python_callable=by_southeast
        )
    
    with TaskGroup('grouping') as grouping:
        task6=PythonOperator(
            task_id='groupby_smoker_',
            python_callable=groupby_smoker
        )

reading_data_processisng_data>>Label('Cleaned_data')>>task3>>Label('Branching with condition')>>[filtering,grouping]