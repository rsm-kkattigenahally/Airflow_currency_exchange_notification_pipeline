# USD to INR Exchange Rate Notifier (Apache Airflow + Docker)

This project implements a daily ETL pipeline using Apache Airflow (v3.x) running on Docker that:

- Fetches the USD to INR exchange rate daily from [Fixer.io](https://fixer.io)
- Stores the rate in a local CSV log
- Sends an email alert (via Mailtrap SMTP) if the rate drops compared to the previous day

---

## Tech Stack

- Apache Airflow 3.x
- Docker + Docker Compose
- Fixer.io API for exchange rates
- Mailtrap SMTP for email testing
- Python + Pandas

---

## Project Structure

```
.
├── dags/
│   └── currency_exg_notify.py         # DAG definition
├── data/
│   └── exchange_rate_log.csv         # Historical rate log
├── config/
│   └── airflow.cfg                   # Optional custom config
├── docker-compose.yaml               # Airflow + dependencies
└── README.md
```

---

## Setup Instructions

### 1. Prerequisites

- Install Docker Desktop: https://www.docker.com/products/docker-desktop
- Clone this repository:

```bash
git clone https://github.com/your-username/exchange-rate-notifier.git
cd exchange-rate-notifier
```

---

### 2. Prepare Directory Structure

Create necessary folders:

```bash
mkdir -p dags data config logs plugins
```

---

### 3. Configure Fixer.io API Key

1. Sign up at https://fixer.io and get your API key.
2. Add it to Airflow as a variable:

```bash
docker exec -it airflow-airflow-scheduler-1 \
  airflow variables set FIXER_API_KEY your_api_key_here
```

---

### 4. Set Up Mailtrap SMTP Connection

1. Sign up at https://mailtrap.io
2. Get your SMTP credentials and inbox email (e.g., abc@inbox.mailtrap.io)
3. Add a secure SMTP connection to Airflow:

```bash
docker exec -it airflow-airflow-scheduler-1 \
  airflow connections add smtp_mailtrap \
  --conn-type smtp \
  --conn-host sandbox.smtp.mailtrap.io \
  --conn-login YOUR_USERNAME \
  --conn-password YOUR_PASSWORD \
  --conn-port 587 \
  --conn-extra '{"mail_from": "your@inbox.mailtrap.io", "smtp_starttls": true, "smtp_ssl": false}'
```

---

### 5. Clear [smtp] Block in airflow.cfg

To ensure Airflow doesn’t use default (unauthenticated) settings, edit config/airflow.cfg:

```ini
[smtp]
smtp_host =
smtp_starttls =
smtp_ssl =
smtp_user =
smtp_password =
smtp_port =
smtp_mail_from =
```

---

### 6. Create Initial CSV File

In the data/ folder, create:

```csv
date,rate
2025-06-07,83.22
```

Make sure this data/ folder is mounted correctly in docker-compose.yaml.

---

### 7. Start Airflow

Start Airflow from scratch:

```bash
docker-compose down --volumes --remove-orphans
docker-compose up airflow-init
docker-compose up -d
```

Then open the UI at: http://localhost:8080  
Login with:
- Username: airflow
- Password: airflow

---


## DAG Logic Summary

- Fetches current rate via Fixer API (EUR → INR due to free plan)
- Logs rate to CSV (exchange_rate_log.csv)
- Sends email alert if today's rate < yesterday's rate
- Uses `send_email_smtp()` with `conn_id='smtp_mailtrap'`

---
## Author

Developed by Komal Nagaraj Kattigenahally  
kkattigenahally@ucsd.edu
