# backend/ml/features/build_survival_episodes.py
from __future__ import annotations
import polars as pl
from datetime import datetime
from backend.ml.features.build_static_features import build_static_features
from backend.ml.features.build_rolling_features import build_rolling_features


def build_survival_episodes(
    breakdown_logs: pl.DataFrame,   # từ corrugating.fact_machine_breakdown_logs
    production_logs: pl.DataFrame,  # từ corrugating.fact_production_logs
    machines: pl.DataFrame,         # từ corrugating.dim_machines
    as_of_date: datetime,
) -> pl.DataFrame:
    """
    Với mỗi máy: cắt lịch sử thành các episode giữa 2 lần hỏng liên tiếp.
    Episode cuối cùng của mỗi máy luôn censored (event=0) trừ khi máy
    hỏng đúng vào as_of_date.
    """
    episodes = []

    for machine_id in machines["machine_id"].unique():
        m_breakdowns = (
            breakdown_logs
            .filter(pl.col("machine_id") == machine_id)
            .sort("breakdown_time")
        )
        m_prod = production_logs.filter(pl.col("machine_id") == machine_id)

        # điểm neo đầu tiên: ngày lắp máy hoặc log đầu tiên có
        cursor = m_prod["start_time"].min() if m_prod.height > 0 else None
        if cursor is None:
            continue

        breakdown_rows = m_breakdowns.select(["breakdown_time", "recovery_time"]).to_dicts()
        prior_count = 0

        for row in breakdown_rows:
            bt = row["breakdown_time"]
            rt = row["recovery_time"]

            duration_days = (bt - cursor).total_seconds() / 86400
            if duration_days <= 0:
                continue

            episode_features = _compute_episode_features(
                machine_id=machine_id,
                production_logs=m_prod,
                breakdown_logs=m_breakdowns,
                machines=machines,
                episode_start=cursor,
                prior_breakdown_count=prior_count,
            )
            episodes.append({
                "machine_id": machine_id,
                "episode_start": cursor,
                "episode_end": bt,
                "duration_days": duration_days,
                "event_observed": 1,
                **episode_features,
            })
            prior_count += 1

            # Episode kế tiếp bắt đầu khi máy đã sửa xong (recovery_time),
            # không phải ngay tại thời điểm hỏng. Nếu recovery_time NULL
            # (sự cố chưa xử lý xong trong dữ liệu), tạm dùng breakdown_time
            # để không crash pipeline, nhưng nên rà lại các dòng breakdown
            # thiếu recovery_time trước khi build lại toàn bộ episode.
            cursor = rt if rt is not None else bt

        # episode cuối: censored, kéo dài tới as_of_date
        final_duration = (as_of_date - cursor).total_seconds() / 86400
        if final_duration > 0:
            episode_features = _compute_episode_features(
                machine_id=machine_id,
                production_logs=m_prod,
                breakdown_logs=m_breakdowns,
                machines=machines,
                episode_start=cursor,
                prior_breakdown_count=prior_count,
            )
            episodes.append({
                "machine_id": machine_id,
                "episode_start": cursor,
                "episode_end": as_of_date,
                "duration_days": final_duration,
                "event_observed": 0,   # censored — quan trọng!
                **episode_features,
            })

    return pl.from_dicts(episodes)


def _compute_episode_features(
    machine_id: int,
    production_logs: pl.DataFrame,
    breakdown_logs: pl.DataFrame,
    machines: pl.DataFrame,
    episode_start: datetime,
    prior_breakdown_count: int,
) -> dict:
    static_feats = build_static_features(
        machines.filter(pl.col("machine_id") == machine_id),
        production_logs, breakdown_logs,
        as_of=episode_start,  # đặc trưng máy TẠI THỜI ĐIỂM episode bắt đầu, tránh leak
    ).to_dicts()[0]

    rolling_feats = build_rolling_features(
        machine_id, production_logs, breakdown_logs,
        as_of=episode_start,
        windows_days=(7,30,90),  # episode feature dùng window 30d làm đại diện
    )

    return {**static_feats, **rolling_feats, "prior_breakdown_count": prior_breakdown_count}