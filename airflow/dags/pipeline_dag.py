from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime
import os

default_args = {
    "owner": "airflow",
    "start_date": datetime(2024, 1, 1),
    "retries": 1
}

dag = DAG(
    dag_id="german_credit_pipeline",
    default_args=default_args,
    schedule_interval=None,  # Change à "@daily" si tu veux l'automatiser
    catchup=False,
    description="Pipeline ETL German Credit Data",
    tags=["etl", "minio", "sqlite"]
)

# Adapter le chemin ici
script_path = "C:\\Users\\User\\Documents\\COURS\\Pipeline\\Atl_Pipeline\\Lab_Atelier_Deploiment_Pipeline\\MiniLAB_Deploiement_Pipeline\\airflow\\scripts\\pipeline_german_credit.py"

run_pipeline = BashOperator(
    task_id="run_credit_pipeline",
    bash_command=f"python {script_path}",
    dag=dag
)
