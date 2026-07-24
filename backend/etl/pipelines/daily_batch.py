from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import polars as pl

try:
    from backend.etl.extract import APIConfig, APIReader, PostgresReader
    from backend.etl.load import ParquetWriter, PostgresWriter
    from backend.etl.transform import (
        clean_breakdown_logs_df,
        clean_production_logs_df,
        build_training_dataset_df,
    )
except ImportError:  # pragma: no cover - fallback for running from backend folder
    from etl.extract import APIConfig, APIReader, PostgresReader
    from etl.load import ParquetWriter, PostgresWriter
    from etl.transform import (
        clean_breakdown_logs_df,
        clean_production_logs_df,
        build_training_dataset_df,
    )


ROOT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def run_daily_batch(output_path: str | Path | None = None) -> dict[str, Any]:
    """ETL daily end-to-end Polars: extract -> transform (DF) -> load."""
    postgres_reader = PostgresReader.from_env()
    raw_production_logs = postgres_reader.extract_table(
        schema="corrugating",
        table="fact_production_logs",
        columns=["production_log_id", "machine_id", "product_id", "start_time", "end_time"],
        limit=1000,
    )
    raw_breakdown_logs = postgres_reader.extract_table(
        schema="corrugating",
        table="fact_machine_breakdown_logs",
        columns=["breakdown_log_id", "machine_id", "breakdown_time", "recovery_time"],
        limit=1000,
    )
    postgres_reader.close()

    production_frame = pl.from_dicts(raw_production_logs)
    breakdown_frame = pl.from_dicts(raw_breakdown_logs)

    cleaned_production = clean_production_logs_df(production_frame)
    cleaned_breakdown = clean_breakdown_logs_df(breakdown_frame)

    training_frame = build_training_dataset_df(cleaned_production, cleaned_breakdown)

    parquet_writer = ParquetWriter(OUTPUT_DIR)
    parquet_path = parquet_writer.write("training_breakdown_risk", training_frame.to_dicts())

    loaded_row_count = 0
    load_to_postgres = os.getenv("ETL_LOAD_TO_POSTGRES", "false").lower() == "true"
    if load_to_postgres:
        postgres_writer = PostgresWriter.from_env()
        loaded_row_count = postgres_writer.write_rows(
            schema="ml",
            table="training_breakdown_risk",
            rows=training_frame.to_dicts(),
            mode="replace",
        )
        postgres_writer.close()

    payload: dict[str, Any] = {
        "raw_production_count": len(raw_production_logs),
        "raw_breakdown_count": len(raw_breakdown_logs),
        "training_row_count": training_frame.height,
        "parquet_path": str(parquet_path),
        "postgres_loaded_rows": loaded_row_count,
    }

    api_base_url = os.getenv("ETL_API_BASE_URL")
    if api_base_url:
        api_reader = APIReader(APIConfig(base_url=api_base_url, token=os.getenv("ETL_API_TOKEN")))
        payload["api_health"] = api_reader.request_json("GET", "/health")

    target_path = Path(output_path) if output_path else OUTPUT_DIR / "daily_batch.json"
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return payload


if __name__ == "__main__":
    run_daily_batch()
