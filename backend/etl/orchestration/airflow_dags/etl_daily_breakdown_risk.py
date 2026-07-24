from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import sys

from airflow import DAG
from airflow.operators.python import PythonOperator


REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

from backend.etl.pipelines.daily_batch import run_daily_batch


DAG_ID = "etl_daily_breakdown_risk"


def _run_daily_etl(**context):
    run_date = context["ds_nodash"]
    output_path = REPO_ROOT / "backend" / "etl" / "output" / f"daily_batch_{run_date}.json"
    return run_daily_batch(output_path=output_path)


with DAG(
    dag_id=DAG_ID,
    description="Daily ETL for machine breakdown risk features",
    schedule="0 2 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    default_args={
        "owner": "data-engineering",
        "depends_on_past": False,
        "retries": 2,
        "retry_delay": timedelta(minutes=10),
    },
    tags=["etl", "ml", "corrugating"],
) as dag:
    daily_batch_task = PythonOperator(
        task_id="run_daily_breakdown_risk_etl",
        python_callable=_run_daily_etl,
    )

    daily_batch_task
