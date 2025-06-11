@echo off
REM Active l environnement virtuel
call C:\Users\camil\OneDrive - Ifag Paris\Cours\Conception_pipeline\Atelier_deploiement_pipeline\MiniLAB_Deploiement_Pipeline\airflow\.venv\Scripts\activate.bat

REM Déclenche le DAG Airflow
airflow dags trigger german_credit_pipeline
