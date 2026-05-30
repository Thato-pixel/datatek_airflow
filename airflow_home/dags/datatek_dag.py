from datetime import datetime, timedelta
from pathlib import Path
from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import ShortCircuitOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.task_group import TaskGroup

PG_CONN  = Variable.get("pg_conn_id", default_var="postgres_datatek")
SQL_BASE = Variable.get("sql_base_path", default_var="/home/thato/datatek_airflow/airflow_home/sql")

def sql(folder, filename):
    return str(Path(SQL_BASE) / folder / filename)

def check_quarantine(source_table, **context):
    hook = PostgresHook(postgres_conn_id=PG_CONN)
    result = hook.get_first(
        "SELECT COUNT(*) FROM quarantine_records WHERE source = %s AND detected_at >= NOW() - INTERVAL '3 hours'",
        parameters=(source_table,)
    )
    count = result[0] if result else 0
    return count == 0

default_args = {"owner": "datatek", "retries": 1, "retry_delay": timedelta(minutes=5)}

def pg(task_id, sql_path):
    return SQLExecuteQueryOperator(task_id=task_id, conn_id=PG_CONN, sql=sql_path)

with DAG(dag_id="datatek_daily_pipeline", default_args=default_args,
    schedule_interval="0 6 * * *", start_date=datetime(2025, 1, 1),
    catchup=False, max_active_runs=1, tags=["datatek"]) as dag:

    with TaskGroup("quality_checks") as quality_group:
        with TaskGroup("billing_checks") as billing_checks:
            qc_bn = pg("billing_null_check", sql("quality","check_billing_nulls.sql"))
            qc_bd = pg("billing_dupe_check", sql("quality","check_billing_dupes.sql"))
        with TaskGroup("session_checks") as session_checks:
            qc_sn = pg("sessions_null_check", sql("quality","check_sessions_nulls.sql"))
            qc_sd = pg("sessions_dupe_check", sql("quality","check_sessions_dupes.sql"))

    gate_billing  = ShortCircuitOperator(task_id="gate_billing",  python_callable=check_quarantine, op_kwargs={"source_table":"src_billing_transactions"})
    gate_sessions = ShortCircuitOperator(task_id="gate_sessions", python_callable=check_quarantine, op_kwargs={"source_table":"src_network_sessions"})

    with TaskGroup("staging") as staging_group:
        stg_b = pg("load_stg_billing",   sql("staging","stg_billing.sql"))
        stg_s = pg("load_stg_sessions",  sql("staging","stg_sessions.sql"))
        stg_c = pg("load_stg_customers", sql("staging","stg_customers.sql"))

    with TaskGroup("transformations") as transform_group:
        t1 = pg("agg_user_revenue",         sql("transformations","agg_user_revenue.sql"))
        t2 = pg("agg_user_usage",           sql("transformations","agg_user_usage.sql"))
        t3 = pg("agg_monthly_revenue",      sql("transformations","agg_monthly_revenue.sql"))
        t4 = pg("agg_arpu",                 sql("transformations","agg_arpu.sql"))
        t5 = pg("session_buckets",          sql("transformations","session_buckets.sql"))
        t6 = pg("agg_session_distribution", sql("transformations","agg_session_distribution.sql"))
        t3 >> t4
        t5 >> t6

    dw = pg("write_dw_user_analytics", sql("warehouse","dw_user_analytics.sql"))

    billing_checks  >> gate_billing  >> stg_b
    session_checks  >> gate_sessions >> stg_s
    quality_group   >> stg_c
    [stg_b, stg_s, stg_c] >> transform_group
    transform_group >> dw
