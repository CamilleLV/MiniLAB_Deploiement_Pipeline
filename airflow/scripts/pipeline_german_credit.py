import pandas as pd
import requests
import io
import os
import sqlite3
import boto3
from botocore.client import Config
from dotenv import load_dotenv

# === Chargement des variables d’environnement ===
load_dotenv()

# === Variables depuis .env ===
DATA_URL = os.getenv("DATA_URL")
OUTPUT_CSV = os.getenv("OUTPUT_CSV")

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
MINIO_BUCKET = os.getenv("MINIO_BUCKET")

SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH")
SQLITE_TABLE_NAME = os.getenv("SQLITE_TABLE_NAME")

# === Colonnes du dataset (selon la doc UCI) ===
COLUMNS = [
    "Status_Checking_Account", "Duration", "Credit_History", "Purpose",
    "Credit_Amount", "Savings", "Employment", "Installment_Rate", 
    "Personal_Status_Sex", "Other_Debtors", "Residence_Since", "Property", 
    "Age", "Other_Installment_Plans", "Housing", "Existing_Credits", 
    "Job", "Liable_People", "Telephone", "Foreign_Worker", "Target"
]

# === Étape 1 : Extraction ===
def download_data(url: str, columns: list) -> pd.DataFrame:
    print("📥 Téléchargement des données...")
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Erreur lors du téléchargement : {response.status_code}")
    
    data = pd.read_csv(io.StringIO(response.text), 
                       sep=' ', 
                       header=None, 
                       names=columns)
    print("✅ Données téléchargées avec succès.")
    return data

# === Étape 2 : Transformation ===
def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    print("🔄 Transformation des données...")
    
    df['Target'] = df['Target'].map({1: 1, 2: 0})
    
    cat_columns = df.select_dtypes(include='object').columns
    for col in cat_columns:
        df[col] = df[col].astype('category')
    
    print("✅ Transformation terminée.")
    return df

# === Étape 3 : Upload MinIO ===
def upload_to_minio(filename: str, bucket: str):
    print(f"☁️ Upload vers MinIO : {filename} → bucket `{bucket}`")

    s3 = boto3.client('s3',
                      endpoint_url=f"http://{MINIO_ENDPOINT}",
                      aws_access_key_id=MINIO_ACCESS_KEY,
                      aws_secret_access_key=MINIO_SECRET_KEY,
                      config=Config(signature_version='s3v4'),
                      region_name='us-east-1')

    # Créer le bucket si besoin
    buckets = s3.list_buckets()
    if not any(b['Name'] == bucket for b in buckets.get('Buckets', [])):
        print(f"📦 Création du bucket `{bucket}`")
        s3.create_bucket(Bucket=bucket)

    # Upload du fichier
    s3.upload_file(Filename=filename, Bucket=bucket, Key=filename)
    print("✅ Upload terminé.")

# === Étape 4 : Chargement dans SQLite ===
def load_into_sqlite(csv_path: str, db_path: str, table_name: str):
    # Crée le dossier si un chemin est précisé (ex: "data/credit.db")
    dir_name = os.path.dirname(db_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    
    print(f"🗄️ Chargement dans SQLite → table `{table_name}`")
    conn = sqlite3.connect(db_path)
    df = pd.read_csv(csv_path)

    df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()
    print("✅ Chargement terminé dans SQLite.")

# === Pipeline principal ===
if __name__ == "__main__":
    # Vérification des variables d'environnement obligatoires
    required_env_vars = {
        "DATA_URL": DATA_URL,
        "OUTPUT_CSV": OUTPUT_CSV,
        "MINIO_ENDPOINT": MINIO_ENDPOINT,
        "MINIO_ACCESS_KEY": MINIO_ACCESS_KEY,
        "MINIO_SECRET_KEY": MINIO_SECRET_KEY,
        "MINIO_BUCKET": MINIO_BUCKET,
        "SQLITE_DB_PATH": SQLITE_DB_PATH,
        "SQLITE_TABLE_NAME": SQLITE_TABLE_NAME
    }
    missing_vars = [k for k, v in required_env_vars.items() if v is None]
    if missing_vars:
        raise EnvironmentError(f"Les variables d'environnement suivantes sont manquantes : {', '.join(missing_vars)}")

    # Vérification supplémentaire pour éviter le passage de None
    if DATA_URL is None:
        raise ValueError("DATA_URL ne doit pas être None.")
    if OUTPUT_CSV is None:
        raise ValueError("OUTPUT_CSV ne doit pas être None.")
    if MINIO_BUCKET is None:
        raise ValueError("MINIO_BUCKET ne doit pas être None.")
    if SQLITE_DB_PATH is None:
        raise ValueError("SQLITE_DB_PATH ne doit pas être None.")
    if SQLITE_TABLE_NAME is None:
        raise ValueError("SQLITE_TABLE_NAME ne doit pas être None.")

    try: 
        df = download_data(DATA_URL, COLUMNS)
        df_clean = transform_data(df)
        df_clean.to_csv(OUTPUT_CSV, index=False)
        upload_to_minio(OUTPUT_CSV, MINIO_BUCKET)
        load_into_sqlite(OUTPUT_CSV, SQLITE_DB_PATH, SQLITE_TABLE_NAME)
    except Exception as e:
        print("❌ Une erreur est survenue dans le pipeline.")
        raise e

 