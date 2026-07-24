from __future__ import annotations

from typing import Any

import polars as pl


REQUIRED_FIELDS = {
    "production_log_id",
    "machine_id",
    "product_id",
    "start_time",
    "end_time",
}


def clean_production_logs(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not records:
        return []

    frame = pl.from_dicts(records)
    missing_fields = REQUIRED_FIELDS.difference(frame.columns)
    if missing_fields:
        missing_fields_text = ", ".join(sorted(missing_fields))
        raise ValueError(f"production log is missing required fields: {missing_fields_text}")

    frame = frame.with_columns(
        [
            pl.col("production_log_id").cast(pl.Int64),
            pl.col("machine_id").cast(pl.Int64),
            pl.col("product_id").cast(pl.Int64),
            pl.col("start_time").cast(pl.Datetime, strict=False),
            pl.col("end_time").cast(pl.Datetime, strict=False),
        ]
    )

    if frame.filter(pl.col("production_log_id").is_null()).height > 0:
        raise ValueError("production_log_id cannot be null")
    if frame.filter(pl.col("machine_id").is_null()).height > 0:
        raise ValueError("machine_id cannot be null")
    if frame.filter(pl.col("product_id").is_null()).height > 0:
        raise ValueError("product_id cannot be null")
    if frame.filter(pl.col("start_time").is_null()).height > 0:
        raise ValueError("start_time cannot be null")
    if frame.filter(pl.col("end_time").is_not_null() & (pl.col("end_time") < pl.col("start_time"))).height > 0:
        raise ValueError("end_time cannot be earlier than start_time")

    cleaned_frame = frame.with_columns(
        [
            pl.when(pl.col("end_time").is_not_null())
            .then(((pl.col("end_time") - pl.col("start_time")).dt.total_seconds() / 60.0).round(2))
            .otherwise(None)
            .alias("duration_minutes")
        ]
    ).select(
        [
            "production_log_id",
            "machine_id",
            "product_id",
            "start_time",
            "end_time",
            "duration_minutes",
        ]
    )

    return cleaned_frame.to_dicts()
