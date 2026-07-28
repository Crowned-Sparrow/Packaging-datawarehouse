# backend/ml/training/train_cox_static.py
from __future__ import annotations

import logging
from pathlib import Path

import joblib
import pandas as pd
from lifelines import CoxPHFitter
from lifelines.utils import k_fold_cross_validation

logger = logging.getLogger(__name__)

FEATURE_COLS = [
    "machine_age_days",
    "prior_breakdown_count",
    "lifetime_avg_downtime_minutes",
    "runs_30d",
    "utilization_30d",
    "waste_ratio_30d",
    "breakdown_count_90d",
]
CATEGORICAL_COLS = ["flute_type"]
 
REQUIRED_COLS = FEATURE_COLS + CATEGORICAL_COLS + ["duration_days", "event_observed"]


def encode_features(df: pd.DataFrame, dummy_cols: list[str] | None = None) -> pd.DataFrame:
    """
    Encode categorical -> dummy, ép kiểu numeric.
    Dùng chung cho cả train và serving để tránh lệch cột.

    - Lúc train: gọi không truyền dummy_cols, hàm tự phát hiện.
    - Lúc serving: truyền đúng dummy_cols đã lưu từ lúc train, để reindex
      (đảm bảo cùng số cột / cùng thứ tự dù input chỉ có 1 dòng).
    """
    encoded = pd.get_dummies(df, columns=CATEGORICAL_COLS, drop_first=True)

    # get_dummies ở pandas mới trả bool -> ép về int cho chắc, lifelines cần numeric thuần
    bool_cols = encoded.select_dtypes(include="bool").columns
    encoded[bool_cols] = encoded[bool_cols].astype(int)

    if dummy_cols is not None:
        # đảm bảo có đủ và đúng thứ tự cột như lúc train; cột thiếu -> điền 0
        for col in dummy_cols:
            if col not in encoded.columns:
                encoded[col] = 0
        encoded = encoded[dummy_cols]

    return encoded


def _validate_input(df: pd.DataFrame) -> pd.DataFrame:
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Thiếu cột bắt buộc trong input: {missing}")

    before = len(df)
    df = df.dropna(subset=REQUIRED_COLS)
    dropped = before - len(df)
    if dropped > 0:
        logger.warning(
            "Đã loại %d/%d dòng do thiếu dữ liệu (NaN) ở feature bắt buộc.",
            dropped, before,
        )

    df = df[df["duration_days"] > 0]
    if len(df) < 20:
        logger.warning(
            "Chỉ còn %d episode sau khi lọc — quá ít để Cox model ổn định (khuyến nghị >= vài chục event).",
            len(df),
        )
    return df


def train(
    df: pd.DataFrame,
    artifact_path: str = "backend/ml/artifacts/cox_model.pkl",
    penalizer: float = 0.1,
    run_cv: bool = True,
) -> CoxPHFitter:
    df = _validate_input(df)

    df_encoded = encode_features(df)
    feature_cols = FEATURE_COLS + [
        c for c in df_encoded.columns if c.startswith("flute_type_")
    ]
    model_df = df_encoded[feature_cols + ["duration_days", "event_observed"]]

    cph = CoxPHFitter(penalizer=penalizer)
    cph.fit(model_df, duration_col="duration_days", event_col="event_observed")

    cph.print_summary()  # hazard ratio + p-value từng feature

    # Kiểm tra giả định Proportional Hazards — bắt buộc phải làm với Cox.
    # Lưu ý: hàm này in cảnh báo ra console/log, không return bool, nên
    # cần đọc kỹ output khi chạy để biết feature nào vi phạm giả định.
    try:
        cph.check_assumptions(model_df, p_value_threshold=0.05, show_plots=False)
    except Exception as exc:  # lifelines có thể raise nếu vi phạm nghiêm trọng
        logger.warning("Giả định Proportional Hazards có thể bị vi phạm: %s", exc)

    if run_cv:
        # QUAN TRỌNG: k_fold_cross_validation tự fit 5 model MỚI trên từng fold,
        # KHÔNG phải đánh giá lại con `cph` đã fit ở trên. Đây là cách đánh giá
        # đúng (tránh leak), nhưng model được LƯU (joblib.dump bên dưới) là model
        # fit trên toàn bộ dữ liệu, không phải model của fold nào.
        scores = k_fold_cross_validation(
            CoxPHFitter(penalizer=penalizer), model_df,
            duration_col="duration_days", event_col="event_observed",
            k=5, scoring_method="concordance_index",
        )
        logger.info("C-index (5-fold CV): %.3f ± %.3f", pd.Series(scores).mean(), pd.Series(scores).std())

    artifact_dir = Path(artifact_path).parent
    artifact_dir.mkdir(parents=True, exist_ok=True)

    joblib.dump(
        {
            "model": cph,
            "feature_cols": feature_cols,          # dùng để reindex lúc serving
            "penalizer": penalizer,
        },
        artifact_path,
    )
    logger.info("Đã lưu model tại %s", artifact_path)

    return cph