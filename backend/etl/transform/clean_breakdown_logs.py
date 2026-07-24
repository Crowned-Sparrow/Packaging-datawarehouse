from __future__ import annotations

from typing import Any

import polars as pl


REQUIRED_FIELDS = {
    "breakdown_log_id",
    "machine_id",
    "breakdown_time",
    "recovery_time",
}


def clean_breakdown_logs(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not records:
        return []

    frame = pl.from_dicts(records)
    missing_fields = REQUIRED_FIELDS.difference(frame.columns)
    if missing_fields:
        missing_fields_text = ", ".join(sorted(missing_fields))
        raise ValueError(f"breakdown log is missing required fields: {missing_fields_text}")

    frame = frame.with_columns(
        [
            pl.col("breakdown_log_id").cast(pl.Int64),
            pl.col("machine_id").cast(pl.Int64),
            pl.col("breakdown_time").cast(pl.Datetime, strict=False),
            pl.col("recovery_time").cast(pl.Datetime, strict=False),
        ]
    )

    if frame.filter(pl.col("breakdown_log_id").is_null()).height > 0:
        raise ValueError("breakdown_log_id cannot be null")
    if frame.filter(pl.col("machine_id").is_null()).height > 0:
        raise ValueError("machine_id cannot be null")
    if frame.filter(pl.col("breakdown_time").is_null()).height > 0:
        raise ValueError("breakdown_time cannot be null")
    if frame.filter(
        pl.col("recovery_time").is_not_null() & (pl.col("recovery_time") < pl.col("breakdown_time"))
    ).height > 0:
        raise ValueError("recovery_time cannot be earlier than breakdown_time")

    cleaned_frame = frame.with_columns(
        [
            pl.when(pl.col("recovery_time").is_not_null())
            .then(((pl.col("recovery_time") - pl.col("breakdown_time")).dt.total_seconds() / 60.0).round(2))
            .otherwise(None)
            .alias("downtime_minutes")
        ]
    ).select(
        [
            "breakdown_log_id",
            "machine_id",
            "breakdown_time",
            "recovery_time",
            "downtime_minutes",
        ]
    )

    return cleaned_frame.to_dicts()
