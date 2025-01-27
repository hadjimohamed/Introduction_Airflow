from datetime import datetime, timedelta
from airflow import DAG 
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from functions import *
import pandas as pd
def get_data():
    postgres_hook=PostgresHook(postgres_conn_id="postgres_connexion")
    connection=postgres_hook.get_conn()
    cursor=connection.cursor()
    query="select * from rental"
    cursor.execute(query)
    rows=cursor.fetchall()
    cols=[desc[0] for desc in cursor.description]
    df=pd.DataFrame(rows,columns=cols)
    cursor.close()
    connection.close()
    return df.to_json()

def group_by(**kwargs):
    ti=kwargs['ti']
    json_data=ti.xcom_pull(task_ids='connection_to_db')
    df=pd.read_json(json_data)
    df_groupby=df.groupby('inventory_id').agg({
        'customer_id':'count'
    }).reset_index()
    df_groupby.to_csv('/opt/airflow/output/rental_goupby.csv',index=False)
default_args={
    'owner':'mohamed'
}

with DAG(
    dag_id='connection_postgre',
    start_date=datetime(2025,1,20),
    schedule_interval='@once'
) as dag:
    task1=PythonOperator(
        task_id='connection_to_db',
        python_callable=get_data
    )
    task2=PythonOperator(
        task_id='groupby_rental',
        python_callable=group_by
    )
    task3=PythonOperator(
        task_id='create_table',
        python_callable=create_table
    )
task1>>task2
task3