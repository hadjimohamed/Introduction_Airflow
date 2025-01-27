from datetime import datetime   
from airflow import DAG 
from airflow.operators.python import PythonOperator
from airflow import DAG 
import pandas as pd
def lire_dataset():
    df=pd.read_csv("/opt/airflow/data/insurance.csv")
    return df.to_json()
def not_null(**kwargs):
    ti=kwargs['ti']
    data_json=ti.xcom_pull(task_ids='load_data')
    df=pd.read_json(data_json)
    df.dropna(inplace=True)
    print(df)
    return df.to_json()
def mean_age(**kwargs):
    ti=kwargs['ti']
    data_json=ti.xcom_pull(task_ids='not_null')
    df=pd.read_json(data_json)
    moyenne_age=df['age'].mean()
    return moyenne_age
def groupby_smoker(**kwargs):
    ti=kwargs['ti']
    data_json=ti.xcom_pull(task_ids='not_null')
    df=pd.read_json(data_json)
    smoker_df=df.groupby('smoker').agg({
        'age':'mean',
        'bmi':'mean',
        'charges':'mean'
    }).reset_index()
    smoker_df.to_csv('/opt/airflow/output/groupby_somker.csv',index=False)
def groupby_region(**kwargs):
    ti=kwargs['ti']
    data_json=ti.xcom_pull(task_ids='not_null')
    df=pd.read_json(data_json)
    region_df=df.groupby('region').agg({
        'age':'mean',
        'bmi':'mean',
        'charges':'mean'
    }).reset_index()
    region_df.to_csv("/opt/airflow/output/groupby_region.csv",index=False)
with DAG(
    dag_id='Data_Pipeline',
    start_date=datetime(2025,1,19),
    schedule_interval='@once'
)as dag:
    task1=PythonOperator(
        task_id='load_data',
        python_callable=lire_dataset
    )
    task2=PythonOperator(
        task_id='not_null',
        python_callable=not_null
    )
    task3=PythonOperator(
        task_id='mean_age',
        python_callable=mean_age
    )
    task4=PythonOperator(
        task_id='agg_smoker',
        python_callable=groupby_smoker
    )
    task5=PythonOperator(
        task_id='agg_region',
        python_callable=groupby_region
    )
task1>>task2>>[task3,task4,task5]