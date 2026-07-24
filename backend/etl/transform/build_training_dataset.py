from __future__ import annotations

from typing import Any

import polars as pl


def _empty_feature_frame() -> pl.DataFrame:
    return pl.DataFrame(
        schema={
            "feature_date": pl.Date,
            "machine_id": pl.Int64,
            "total_runs": pl.Int64, # tổng số lần chạy
            "total_production_minutes": pl.Float64, # tổng thời gian chạy
            "breakdown_count": pl.Int64,    # số lần hỏng máy
            "downtime_minutes": pl.Float64, # thời gian hỏng
        }
    )


def build_training_dataset(
    production_logs: list[dict[str, Any]],
    breakdown_logs: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    production_features = _empty_feature_frame()
    if production_logs:
        production_frame = pl.from_dicts(production_logs).with_columns(
            [
                pl.col("machine_id").cast(pl.Int64),
                pl.col("start_time").cast(pl.Datetime, strict=False),
                pl.col("duration_minutes").cast(pl.Float64, strict=False),
            ]
        )
        production_features = (
            production_frame.with_columns(pl.col("start_time").dt.date().alias("feature_date"))
            .group_by(["feature_date", "machine_id"])
            .agg(
                [
                    pl.len().alias("total_runs"),
                    pl.col("duration_minutes").fill_null(0.0).sum().round(2).alias("total_production_minutes"),
                ]
            )
            .with_columns(
                [
                    pl.lit(0, dtype=pl.Int64).alias("breakdown_count"),
                    pl.lit(0.0, dtype=pl.Float64).alias("downtime_minutes"),
                ]
            )
            .select(_empty_feature_frame().columns)
        )

    breakdown_features = _empty_feature_frame()
    if breakdown_logs:
        breakdown_frame = pl.from_dicts(breakdown_logs).with_columns(
            [
                pl.col("machine_id").cast(pl.Int64),
                pl.col("breakdown_time").cast(pl.Datetime, strict=False),
                pl.col("downtime_minutes").cast(pl.Float64, strict=False),
            ]
        )
        breakdown_features = (
            breakdown_frame.with_columns(pl.col("breakdown_time").dt.date().alias("feature_date"))
            .group_by(["feature_date", "machine_id"])
            .agg(
                [
                    pl.len().alias("breakdown_count"),
                    pl.col("downtime_minutes").fill_null(0.0).sum().round(2).alias("downtime_minutes"),
                ]
            )
            .with_columns(
                [
                    pl.lit(0, dtype=pl.Int64).alias("total_runs"),
                    pl.lit(0.0, dtype=pl.Float64).alias("total_production_minutes"),
                ]
            )
            .select(_empty_feature_frame().columns)
        )

    combined = pl.concat([production_features, breakdown_features], how="vertical_relaxed")

    dataset_frame = (
        combined.group_by(["feature_date", "machine_id"])
        .agg(
            [
                pl.col("total_runs").sum().alias("total_runs"),
                pl.col("total_production_minutes").sum().round(2).alias("total_production_minutes"),
                pl.col("breakdown_count").sum().alias("breakdown_count"),
                pl.col("downtime_minutes").sum().round(2).alias("downtime_minutes"),
            ]
        )
        .with_columns(
            [
                pl.when(pl.col("total_runs") > 0)
                .then((pl.col("total_production_minutes") / pl.col("total_runs")).round(2))
                .otherwise(0.0)
                .alias("avg_run_minutes"),
                pl.when(pl.col("breakdown_count") > 0).then(1).otherwise(0).alias("label_has_breakdown"),
            ]
        )
        .select(
            [
                "feature_date",
                "machine_id",
                "total_runs",
                "total_production_minutes",
                "avg_run_minutes",
                "breakdown_count",
                "downtime_minutes",
                "label_has_breakdown",
            ]
        )
        .sort(["feature_date", "machine_id"])
    )

    return dataset_frame.to_dicts()
