from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

try:
    from backend.etl.extract import APIConfig, APIReader, PostgresReader
except ImportError:  # pragma: no cover - fallback for running from backend folder
    from etl.extract import APIConfig, APIReader, PostgresReader


ROOT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def run_daily_batch(output_path: str | Path | None = None) -> dict[str, Any]:
    """Mẫu ETL daily: extract từ PostgreSQL + API, lưu JSON ra file."""
    payload: dict[str, Any] = {}

    try:
        postgres_reader = PostgresReader.from_env()
        payload["production_logs"] = postgres_reader.extract_table(
            schema="corrugating",
            table="fact_production_logs",
            columns=["production_log_id", "machine_id", "product_id", "start_time", "end_time"],
            limit=100,
        )
        payload["breakdown_logs"] = postgres_reader.extract_table(
            schema="corrugating",
            table="fact_machine_breakdown_logs",
            columns=["breakdown_log_id", "machine_id", "breakdown_time", "recovery_time"],
            limit=100,
        )
        postgres_reader.close()
    except Exception as exc:  # pragma: no cover - depends on runtime env
        payload["postgres_error"] = str(exc)

    api_base_url = os.getenv("ETL_API_BASE_URL")
    if api_base_url:
        try:
            api_reader = APIReader(APIConfig(base_url=api_base_url, token=os.getenv("ETL_API_TOKEN")))
            payload["api_health"] = api_reader.request_json("GET", "/health")
        except Exception as exc:  # pragma: no cover - depends on runtime env
            payload["api_error"] = str(exc)

    target_path = Path(output_path) if output_path else OUTPUT_DIR / "daily_batch.json"
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return payload


if __name__ == "__main__":
    run_daily_batch()
