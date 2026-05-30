from google.cloud import bigquery
import psycopg2
import os
import pandas as pd

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/thato/datatek_airflow/keys/bigquery_key.json"

print("Reading from PostgreSQL...")
pg_conn = psycopg2.connect(
    host="localhost", dbname="datatek_db",
    user="postgres", password="postgres123"
)
df = pd.read_sql("SELECT * FROM dw_user_analytics", pg_conn)
pg_conn.close()
print(f"Read {len(df)} rows from PostgreSQL")

# Save to CSV
df.to_csv("/tmp/dw_user_analytics.csv", index=False)
print("Saved to CSV")

# Load to BigQuery via CSV
client = bigquery.Client(project="public-subproject2")
table_id = "public-subproject2.datatek_warehouse.dw_user_analytics"

job_config = bigquery.LoadJobConfig(
    source_format=bigquery.SourceFormat.CSV,
    skip_leading_rows=1,
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    autodetect=True,
)

with open("/tmp/dw_user_analytics.csv", "rb") as f:
    load_job = client.load_table_from_file(f, table_id, job_config=job_config)

load_job.result()
print(f"Successfully loaded {load_job.output_rows} rows to BigQuery!")
