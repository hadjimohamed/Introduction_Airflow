from airflow.providers.postgres.hooks.postgres import PostgresHook
from random import choice
import pandas as pd
from airflow.models import Variable
#postgre.py
def create_table():
    postgres_hook = PostgresHook(postgres_conn_id="postgres_connexion")
    connection = postgres_hook.get_conn()
    cursor = connection.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS test (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    cursor.execute(create_table_query)
    connection.commit()
    cursor.close()
    connection.close()
#-------------------------------------------------------------------------#
#branching.py
def has_driving():
    return choice([True,False])

def branch(ti):
    if ti.xcom_pull(task_ids="return_stat_driving_licence"):
        return 'can_drive'
    else:
        return 'cant_drive'

def eligible_for_driving():
    print("Yay ! you are eligible for driving")

def note_eligible_for_driving():
    print("Non ! You are note eligible for driving")

#-----------------------------------------------------------------------------#
#branching_variabes.py
path_data="/opt/airflow/data/insurance.csv"
def get_data():
    df=pd.read_csv(path_data)
    return df.to_json()

def drop_null(**kwargs):
    ti=kwargs['ti']
    json_data=ti.xcom_pull(task_ids='read_dataset')
    df=pd.read_json(json_data)
    df.dropna(inplace=True)
    return df.to_json()

def branch():
    action=Variable.get("my_variable",default_var=None)
    if action.startswith('filter'):
        return action 
    elif action=='groupby_smoker_region':
        return 'groupby_smoker_region'

def filter_by_southwest(**kwargs):
    ti=kwargs['ti']
    json_data=ti.xcom_pull(task_ids='drop_null')
    df=pd.read_json(json_data)
    data=df[df['region']=='southwest']
    return data.to_json()

def filter_by_southest(**kwargs):
    ti=kwargs['ti']
    json_data=ti.xcom_pull(task_ids='drop_null')
    df=pd.read_json(json_data)
    data=df[df['region']=='southest']
    return data.to_json()

def groupby_smoker(**kwargs):
    ti=kwargs['ti']
    data_json=ti.xcom_pull(task_ids='drop_null')
    df=pd.read_json(data_json)
    smoker_df=df.groupby('smoker').agg({
        'age':'mean',
        'bmi':'mean',
        'charges':'mean'
    }).reset_index()
    return smoker_df.to_json()

#---------------------------------------------------------------#
#taskgroups_edgelabes.py
def get_my_data(ti):
    df=pd.read_csv("/opt/airflow/data/insurance.csv")
    ti.xcom_push(key='my_data',value=df.to_json())

def null_values(ti):
    json_data=ti.xcom_pull(key='my_data')
    df=pd.read_json(json_data)
    df.dropna(inplace=True)
    ti.xcom_push(key='drop_null_values',value=df.to_json())

def my_branch():
    action=Variable.get("my_val",default_var=None)
    if action.startswith('filter'):
        return "filtering.{0}".format(action) 
    elif action=='groupby_smoker_':
        return "grouping.{0}".format(action)

def by_southwest(ti):
    json_data=ti.xcom_pull(key='drop_null_values')
    df=pd.read_json(json_data)
    region_dt=df[df['region']=='southwest']
    ti.xcom_push(key='southest',value=region_dt.to_json())

def by_southeast(ti):
    json_data=ti.xcom_pull(key='drop_null_values')
    df=pd.read_json(json_data)
    region_dt=df[df['region']=='southeast']
    ti.xcom_push(key='southeast',value=region_dt.to_json())

def groupby_smoker(ti):
    json_data=ti.xcom_pull(key='drop_null_values')
    df=pd.read_json(json_data)
    df_grpupby=df.groupby('smoker').agg({
        'age':'mean',
        'charges':'mean'
    }).reset_index()
    ti.xcom_push(key='groupby',value=df_grpupby.to_json())
