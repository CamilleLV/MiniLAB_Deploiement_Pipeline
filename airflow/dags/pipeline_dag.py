from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime
import os
from dotenv import load_dotenv

# === Chargement des variables d’environnement ===
load_dotenv()

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
PIPELINE_SCRIPT_PATH = os.getenv("PIPELINE_SCRIPT_PATH", "airflow/scripts/pipeline_german_credit.py")

run_pipeline = BashOperator(
    task_id="run_credit_pipeline",
    bash_command=f"python {PIPELINE_SCRIPT_PATH}",
    dag=dag
)
