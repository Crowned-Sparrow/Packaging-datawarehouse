# backend/ml/serving/predictor.py — cập nhật
import joblib
import pandas as pd
from pathlib import Path

from backend.ml.training.train_cox_static import encode_features

ARTIFACT_PATH = Path(__file__).resolve().parents[1] / "artifacts" / "cox_model.pkl"
_cph = None
_feature_cols = None


def _ensure_loaded():
    global _cph, _feature_cols
    if _cph is not None and _feature_cols is not None:
        return _cph, _feature_cols

    if not ARTIFACT_PATH.exists():
        raise FileNotFoundError(f"Không tìm thấy model artifact: {ARTIFACT_PATH}")

    artifact = joblib.load(ARTIFACT_PATH)
    if "model" not in artifact or "feature_cols" not in artifact:
        raise KeyError("Model artifact thiếu key bắt buộc: 'model' hoặc 'feature_cols'")

    _cph = artifact["model"]
    _feature_cols = artifact["feature_cols"]
    return _cph, _feature_cols


def predict_risk(current_features: dict) -> dict:
    cph, feature_cols = _ensure_loaded()
    raw_df = pd.DataFrame([current_features])
    row = encode_features(raw_df, dummy_cols=feature_cols)  # đảm bảo khớp cột với lúc train

    median_days = cph.predict_median(row).values[0]
    partial_hazard = cph.predict_partial_hazard(row).values[0]

    return {
        "median_days_to_breakdown": None if pd.isna(median_days) else round(float(median_days), 1),
        "relative_risk_score": round(float(partial_hazard), 3),
    }