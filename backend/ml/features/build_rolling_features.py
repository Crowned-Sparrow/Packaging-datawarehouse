# backend/ml/features/build_rolling_features.py
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import polars as pl

DEFAULT_WINDOWS_DAYS = (7, 30, 90)


def build_rolling_features(
    machine_id: int,
    production_logs: pl.DataFrame,   # đã lọc sẵn machine_id nếu muốn, hoặc để nguyên rồi filter trong hàm
    breakdown_logs: pl.DataFrame,
    as_of: datetime,
    windows_days: tuple[int, ...] = DEFAULT_WINDOWS_DAYS,
) -> dict[str, Any]:
    """
    Tính rolling feature cho 1 máy tại thời điểm as_of, với các window N ngày.
    CHỈ dùng dữ liệu start_time/breakdown_time < as_of để tránh leak tương lai.

    Output là 1 dict phẳng, ví dụ với windows=(7,30,90):
        runs_7d, runs_30d, runs_90d,
        utilization_7d, utilization_30d, utilization_90d,
        waste_ratio_7d, waste_ratio_30d, waste_ratio_90d,
        breakdown_count_7d, breakdown_count_30d, breakdown_count_90d,
        downtime_minutes_7d, downtime_minutes_30d, downtime_minutes_90d,
    """
    prod_m = production_logs.filter(
        (pl.col("machine_id") == machine_id) & (pl.col("start_time") < as_of)
    )
    breakdown_m = breakdown_logs.filter(
        (pl.col("machine_id") == machine_id) & (pl.col("breakdown_time") < as_of)
    )

    features: dict[str, Any] = {}

    for window in windows_days:
        window_start = as_of - timedelta(days=window)
        suffix = f"{window}d"

        prod_window = prod_m.filter(pl.col("start_time") >= window_start)
        breakdown_window = breakdown_m.filter(pl.col("breakdown_time") >= window_start)

        features.update(
            _compute_production_window_features(prod_window, window, suffix)
        )
        features.update(
            _compute_breakdown_window_features(breakdown_window, suffix)
        )

    return features


def _compute_production_window_features(
    prod_window: pl.DataFrame, window_days: int, suffix: str
) -> dict[str, Any]:
    """Feature liên quan tới sản lượng/vận hành trong window."""
    total_runs = prod_window.height
    if total_runs == 0:
        return {
            f"runs_{suffix}": 0,
            f"utilization_{suffix}": 0.0,
            f"waste_ratio_{suffix}": 0.0,
            f"avg_cut_pallet_{suffix}": 0.0,
        }

    # Duration mỗi run (phút) — nếu chưa có cột duration_minutes sẵn thì tính từ start/end
    durations = (
        pl.when(pl.col("end_time").is_not_null())
        .then((pl.col("end_time") - pl.col("start_time")).dt.total_seconds() / 60.0)
        .otherwise(0.0)
    )
    prod_window = prod_window.with_columns(durations.alias("_duration_minutes"))

    total_minutes = prod_window["_duration_minutes"].sum()
    window_capacity_minutes = window_days * 24 * 60
    utilization = round(total_minutes / window_capacity_minutes, 4) if window_capacity_minutes > 0 else 0.0

    # Waste ratio: tổng phế liệu / tổng khối lượng sản phẩm tốt trong window
    total_product_weight = prod_window["product_weight"].fill_null(0).sum()
    total_waste = (
        prod_window["waste_endroll_weight"].fill_null(0).sum()
        + prod_window["waste_trim_weight"].fill_null(0).sum()
        + prod_window["waste_production_weight"].fill_null(0).sum()
        + prod_window["waste_core_weight"].fill_null(0).sum()
    )
    waste_ratio = round(total_waste / total_product_weight, 4) if total_product_weight > 0 else 0.0

    avg_cut_pallet = prod_window["cut_pallet_count"].fill_null(0).mean() or 0.0

    return {
        f"runs_{suffix}": total_runs,
        f"utilization_{suffix}": min(utilization, 1.0),
        f"waste_ratio_{suffix}": waste_ratio,
        f"avg_cut_pallet_{suffix}": round(float(avg_cut_pallet), 2),
    }


def _compute_breakdown_window_features(
    breakdown_window: pl.DataFrame, suffix: str
) -> dict[str, Any]:
    """Feature liên quan tới sự cố trong window."""
    count = breakdown_window.height
    if count == 0:
        return {
            f"breakdown_count_{suffix}": 0,
            f"downtime_minutes_{suffix}": 0.0,
        }

    downtime = (
        breakdown_window
        .filter(pl.col("recovery_time").is_not_null())
        .with_columns(
            (
                (pl.col("recovery_time") - pl.col("breakdown_time")).dt.total_seconds() / 60.0
            ).alias("_downtime_minutes")
        )["_downtime_minutes"]
        .sum()
    )

    return {
        f"breakdown_count_{suffix}": count,
        f"downtime_minutes_{suffix}": round(float(downtime or 0.0), 2),
    }