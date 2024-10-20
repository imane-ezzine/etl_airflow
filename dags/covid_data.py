import requests
import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator
import datetime

def _extract_covid_data():
    response = requests.get("https://api.covidtracking.com/v1/us/daily.csv")
    with open('covid_data.csv', 'wb') as f:
        f.write(response.content)

def _pre_process():
    df = pd.read_csv('covid_data.csv')  # Charger les données
    df = df[df.states == 56]  # Conserver uniquement les données des états 56
    # Supprimer les colonnes inutiles
    df = df.drop(columns=['recovered', 'lastModified', 'states', 'dateChecked', 'total', 'posNeg', 'hospitalized'])
    # Renommer les colonnes
    df.rename(columns={
        "negative": "pcr_test_negative",
        "positive": "pcr_test_positive"
    }, inplace=True)
    # Convertir la date en format datetime
    df["date"] = df.date.astype('str')
    df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
    # Supprimer les valeurs manquantes
    df = df.dropna()
    # Exporter vers un fichier CSV
    df.to_csv("/opt/airflow/data/clean_covid_data.csv", index=False)

default_args = {
    'start_date': datetime.datetime(2023, 8, 30)
}

with DAG(dag_id="load_covid_data", catchup=False, schedule_interval="@daily", default_args=default_args) as dag:

    # Tâche #1 - Extraire les données de l'API
    extract_data = PythonOperator(
        task_id="extract_data",
        python_callable=_extract_covid_data
    )

    # Tâche #2 - Nettoyer les données
    pre_process = PythonOperator(
        task_id="pre_process",
        python_callable=_pre_process
    )

    # Dépendances
    extract_data >> pre_process
