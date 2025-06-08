
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.utils.email import send_email_smtp
from airflow.models import Variable
from datetime import datetime, timedelta
import requests
import pandas as pd
import os

API_KEY = Variable.get("FIXER_API_KEY")
#print(API_KEY)
URL = f"http://data.fixer.io/api/latest?access_key={API_KEY}&base=EUR&symbols=INR"
#print(URL)
DATA_PATH = 'dags/data/exchange_rate_log.csv'

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

dag = DAG(
    dag_id='usd_inr_exchange_notifier',
    default_args=default_args,
    start_date=datetime(2025, 6, 8, 0, 0),
    schedule='@daily',
    catchup=False
)

def fetch_exchange_rate():
    resp = requests.get(URL)
    data = resp.json()
    if resp.status_code != 200 or 'error' in data:
        raise Exception(f"Error fetching exchange rate: {data.get('error', {}).get('info', 'Unknown error')}")
    
    rate = data['rates']['INR']
    today = datetime.now().strftime('%Y-%m-%d')
    new_row = pd.DataFrame([[today, rate]], columns=['date', 'rate'])

    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        df = new_row

    df.to_csv(DATA_PATH, index=False)

def check_rate_drop_and_notify(**kwargs):
    if not os.path.exists(DATA_PATH):
        return

    df = pd.read_csv(DATA_PATH)
    if len(df) < 2:
        return

    yesterday_rate = df.iloc[-2]['rate']
    today_rate = df.iloc[-1]['rate']

    if today_rate < yesterday_rate:
        subject = "[Alert] USD to INR Exchange Rate Dropped"
        content = f"<b>Rate dropped</b>: {yesterday_rate:.2f} ➝ {today_rate:.2f}"
        send_email_smtp(
            to=["<your email>"],
            subject=subject,
            html_content=content,
            conn_id="smtp_mailtrap"
        )

fetch_task = PythonOperator(
    task_id='fetch_rate',
    python_callable=fetch_exchange_rate,
    dag=dag
)

check_task = PythonOperator(
    task_id='check_drop',
    python_callable=check_rate_drop_and_notify,
    dag=dag
)

fetch_task >> check_task
