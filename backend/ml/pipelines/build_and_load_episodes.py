# backend/ml/pipelines/build_and_load_episodes.py
from __future__ import annotations

import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import polars as pl
try:
    from backend.etl.extract import PostgresReader
    from backend.etl.load import PostgresWriter
    from backend.ml.features.build_survival_episodes import build_survival_episodes
except ImportError:  # pragma: no cover - fallback khi chạy trực tiếp từ backend/
    from etl.extract import PostgresReader
    from etl.load import PostgresWriter
    from ml.features.build_survival_episodes import build_survival_episodes

logger = logging.getLogger(__name__)

MACHINES_COLUMNS = ["machine_id", "flute_type"]

PRODUCTION_COLUMNS = [
    "machine_id",
    "start_time",
    "end_time",
    "product_weight",
    "waste_endroll_weight",
    "waste_trim_weight",
    "waste_production_weight",
    "waste_core_weight",
    "cut_pallet_count",
]

BREAKDOWN_COLUMNS = ["machine_id", "breakdown_time", "recovery_time"]

TARGET_SCHEMA = "ml"
TARGET_TABLE = "machine_survival_episodes"


def _to_frame(rows: list[dict[str, Any]], schema: dict[str, Any]) -> pl.DataFrame:
    """pl.from_dicts() lỗi schema khi rows rỗng, nên luôn ép schema tường minh."""
    if not rows:
        return pl.DataFrame(schema=schema)
    return pl.from_dicts(rows, schema=schema)


def _load_source_frames() -> tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame]:
    reader = PostgresReader.from_env()
    try:
        raw_machines = reader.extract_table(
            schema="corrugating", table="dim_machines", columns=MACHINES_COLUMNS
        )
        raw_production = reader.extract_table(
            schema="corrugating", table="fact_production_logs", columns=PRODUCTION_COLUMNS
        )
        raw_breakdowns = reader.extract_table(
            schema="corrugating", table="fact_machine_breakdown_logs", columns=BREAKDOWN_COLUMNS
        )
    finally:
        reader.close()

    machines = _to_frame(
        raw_machines, {"machine_id": pl.Int64, "flute_type": pl.Utf8}
    )
    production_logs = _to_frame(
        raw_production,
        {
            "machine_id": pl.Int64,
            "start_time": pl.Datetime,
            "end_time": pl.Datetime,
            "product_weight": pl.Float64,
            "waste_endroll_weight": pl.Float64,
            "waste_trim_weight": pl.Float64,
            "waste_production_weight": pl.Float64,
            "waste_core_weight": pl.Float64,
            "cut_pallet_count": pl.Int64,
        },
    )
    breakdown_logs = _to_frame(
        raw_breakdowns,
        {
            "machine_id": pl.Int64,
            "breakdown_time": pl.Datetime,
            "recovery_time": pl.Datetime,
        },
    )

    logger.info(
        "Loaded machines=%d production_logs=%d breakdown_logs=%d",
        machines.height,
        production_logs.height,
        breakdown_logs.height,
    )
    return machines, production_logs, breakdown_logs


def build_and_load_episodes(
    as_of_date: datetime | None = None,
    mode: str = "replace",
) -> dict[str, Any]:
    """
    Đọc raw production/breakdown logs từ Postgres, dựng survival episodes
    cho từng máy, rồi ghi vào ml.machine_survival_episodes.

    mode: "replace" (mặc định, TRUNCATE rồi insert lại toàn bộ) hoặc
          "append" (chỉ dùng khi chắc chắn không bị trùng episode).
    """
    as_of_date = as_of_date or datetime.now()

    machines, production_logs, breakdown_logs = _load_source_frames()

    if machines.height == 0:
        raise ValueError("Không có máy nào trong corrugating.dim_machines, dừng lại.")
    if production_logs.height == 0:
        raise ValueError("Không có production log nào — không thể dựng episode (cần start_time làm mốc).")

    episodes = build_survival_episodes(
        breakdown_logs=breakdown_logs,
        production_logs=production_logs,
        machines=machines,
        as_of_date=as_of_date,
    )

    if episodes.height == 0:
        logger.warning("Không dựng được episode nào (dữ liệu quá ít hoặc chưa đủ thời gian).")
        return {"episode_count": 0, "loaded_rows": 0}

    # machine_id trong build_survival_episodes lấy từ polars unique() -> ép lại kiểu Python int
    # để tránh lỗi kiểu dữ liệu (numpy int) khi bind params cho psycopg2.
    rows = episodes.to_dicts()
    for row in rows:
        row["machine_id"] = int(row["machine_id"])

    writer = PostgresWriter.from_env()
    try:
        loaded_rows = writer.write_rows(
            schema=TARGET_SCHEMA,
            table=TARGET_TABLE,
            rows=rows,
            mode=mode,
        )
    finally:
        writer.close()

    logger.info("Đã ghi %d episode vào %s.%s (mode=%s)", loaded_rows, TARGET_SCHEMA, TARGET_TABLE, mode)
    return {"episode_count": episodes.height, "loaded_rows": loaded_rows}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build & load machine survival episodes vào ml schema.")
    parser.add_argument(
        "--as-of",
        type=str,
        default=None,
        help="ISO datetime làm mốc censoring cho episode cuối (mặc định: thời điểm hiện tại).",
    )
    parser.add_argument(
        "--mode",
        choices=["replace", "append"],
        default="replace",
        help="replace: TRUNCATE rồi insert lại (khuyến nghị). append: chỉ thêm mới.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    args = _parse_args()
    as_of = datetime.fromisoformat(args.as_of) if args.as_of else None
    result = build_and_load_episodes(as_of_date=as_of, mode=args.mode)
    print(result)