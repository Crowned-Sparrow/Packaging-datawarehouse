# backend/ml/features/build_static_features.py
from __future__ import annotations

from datetime import datetime
from typing import Any

import polars as pl


def build_static_features(
    machines: pl.DataFrame,          # corrugating.dim_machines
    production_logs: pl.DataFrame,   # corrugating.fact_production_logs
    breakdown_logs: pl.DataFrame,    # corrugating.fact_machine_breakdown_logs
    as_of: datetime,
) -> pl.DataFrame:
    """
    Tính các đặc trưng tĩnh / bán tĩnh cho từng máy, tính đến thời điểm as_of.

    Static ở đây nghĩa là: không thay đổi trong nội bộ 1 episode (giữa 2 lần hỏng),
    khác với rolling features (window ngắn hạn, thay đổi liên tục).

    Output: 1 dòng / machine_id, gồm:
        - flute_type            : loại sóng (categorical)
        - machine_age_days       : số ngày kể từ lần ghi nhận đầu tiên của máy
        - lifetime_total_runs    : tổng số lượt sản xuất từ trước tới as_of
        - lifetime_breakdown_count: tổng số lần hỏng từ trước tới as_of
        - lifetime_avg_downtime_minutes: downtime trung bình mỗi lần hỏng (độ nghiêm trọng)
        - days_since_last_breakdown: số ngày kể từ lần hỏng gần nhất (NULL nếu chưa từng hỏng)
    """
    prod_before = production_logs.filter(pl.col("start_time") <= as_of)
    breakdown_before = breakdown_logs.filter(pl.col("breakdown_time") <= as_of)

    # --- 1. Thời điểm "ra đời" của máy: log sản xuất/breakdown sớm nhất quan sát được ---
    # dim_machines không có created_at, nên dùng bản ghi nghiệp vụ sớm nhất làm proxy.
    first_seen = _compute_first_seen(prod_before, breakdown_before, machines)

    # --- 2. Tổng số lượt sản xuất tính đến as_of ---
    lifetime_runs = (
        prod_before.group_by("machine_id")
        .agg(pl.len().alias("lifetime_total_runs"))
    )

    # --- 3. Lịch sử breakdown tính đến as_of ---
    lifetime_breakdowns = (
        breakdown_before
        .with_columns(
            (
                (pl.col("recovery_time") - pl.col("breakdown_time"))
                .dt.total_seconds() / 60.0
            ).alias("downtime_minutes")
        )
        .group_by("machine_id")
        .agg(
            [
                pl.len().alias("lifetime_breakdown_count"),
                pl.col("downtime_minutes").mean().round(2).alias("lifetime_avg_downtime_minutes"),
                pl.col("breakdown_time").max().alias("last_breakdown_time"),
            ]
        )
    )

    # --- 4. Ghép tất cả lại theo machine_id, machine nào chưa có dữ liệu -> điền mặc định ---
    result = (
        machines.select(["machine_id", "flute_type"])
        .join(first_seen, on="machine_id", how="left")
        .join(lifetime_runs, on="machine_id", how="left")
        .join(lifetime_breakdowns, on="machine_id", how="left")
        .with_columns(
            [
                pl.col("lifetime_total_runs").fill_null(0),
                pl.col("lifetime_breakdown_count").fill_null(0),
                pl.col("lifetime_avg_downtime_minutes").fill_null(0.0),
            ]
        )
        .with_columns(
            [
                pl.when(pl.col("first_seen").is_not_null())
                .then(((pl.lit(as_of) - pl.col("first_seen")).dt.total_seconds() / 86400).round(2))
                .otherwise(None)
                .alias("machine_age_days"),

                pl.when(pl.col("last_breakdown_time").is_not_null())
                .then(((pl.lit(as_of) - pl.col("last_breakdown_time")).dt.total_seconds() / 86400).round(2))
                .otherwise(None)
                .alias("days_since_last_breakdown"),
            ]
        )
        .drop(["first_seen", "last_breakdown_time"])
    )

    return result


def _compute_first_seen(
    prod_before: pl.DataFrame,
    breakdown_before: pl.DataFrame,
    machines: pl.DataFrame,
) -> pl.DataFrame:
    """Lấy mốc thời gian sớm nhất mà máy xuất hiện trong dữ liệu (production hoặc breakdown)."""
    prod_first = (
        prod_before.group_by("machine_id")
        .agg(pl.col("start_time").min().alias("first_seen_prod"))
    )
    breakdown_first = (
        breakdown_before.group_by("machine_id")
        .agg(pl.col("breakdown_time").min().alias("first_seen_breakdown"))
    )

    merged = (
        machines.select("machine_id")
        .join(prod_first, on="machine_id", how="left")
        .join(breakdown_first, on="machine_id", how="left")
        .with_columns(
            pl.min_horizontal("first_seen_prod", "first_seen_breakdown").alias("first_seen")
        )
        .select(["machine_id", "first_seen"])
    )
    return merged


def build_static_features_for_machine(
    machine_id: int,
    machines: pl.DataFrame,
    production_logs: pl.DataFrame,
    breakdown_logs: pl.DataFrame,
    as_of: datetime,
) -> dict[str, Any]:
    """Wrapper tiện dùng lúc serving: trả về dict feature cho 1 máy duy nhất."""
    df = build_static_features(
        machines.filter(pl.col("machine_id") == machine_id),
        production_logs.filter(pl.col("machine_id") == machine_id),
        breakdown_logs.filter(pl.col("machine_id") == machine_id),
        as_of=as_of,
    )
    if df.height == 0:
        raise ValueError(f"Không tìm thấy máy machine_id={machine_id}")
    return df.to_dicts()[0]