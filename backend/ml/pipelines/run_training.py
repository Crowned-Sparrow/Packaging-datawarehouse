# backend/ml/pipelines/run_training.py
from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Any

import pandas as pd

try:
    from backend.etl.extract import PostgresReader
    from backend.ml.training.train_cox_static import train, REQUIRED_COLS
except ImportError:  # pragma: no cover - fallback khi chạy trực tiếp từ backend/
    from etl.extract import PostgresReader
    from ml.training.train_cox_static import train, REQUIRED_COLS

logger = logging.getLogger(__name__)

SOURCE_SCHEMA = "ml"
SOURCE_TABLE = "machine_survival_episodes"
DEFAULT_ARTIFACT_PATH = "backend/ml/artifacts/cox_model.pkl"
DEFAULT_MIN_EVENTS = 20  # số episode có event_observed=1 tối thiểu để Cox model ổn định


def _load_episodes() -> pd.DataFrame:
    reader = PostgresReader.from_env()
    try:
        rows: list[dict[str, Any]] = reader.extract_table(
            schema=SOURCE_SCHEMA,
            table=SOURCE_TABLE,
            columns=REQUIRED_COLS,
        )
    finally:
        reader.close()

    if not rows:
        raise ValueError(
            f"Không có dữ liệu trong {SOURCE_SCHEMA}.{SOURCE_TABLE}. "
            "Hãy chạy build_and_load_episodes.py trước."
        )

    df = pd.DataFrame(rows)
    logger.info("Đã đọc %d episode từ %s.%s", len(df), SOURCE_SCHEMA, SOURCE_TABLE)
    return df


def _validate_events(df: pd.DataFrame, min_events: int) -> None:
    event_count = int(df["event_observed"].sum())
    if event_count < min_events:
        raise ValueError(
            f"Chỉ có {event_count} episode có event_observed=1 "
            f"(yêu cầu tối thiểu {min_events}). Cox model sẽ không ổn định, dừng training."
        )
    logger.info("Số episode có event (hỏng máy thực sự): %d / %d", event_count, len(df))


def run_training(
    artifact_path: str = DEFAULT_ARTIFACT_PATH,
    penalizer: float = 0.1,
    run_cv: bool = True,
    min_events: int = DEFAULT_MIN_EVENTS,
) -> dict[str, Any]:
    df = _load_episodes()
    _validate_events(df, min_events=min_events)

    cph = train(
        df,
        artifact_path=artifact_path,
        penalizer=penalizer,
        run_cv=run_cv,
    )

    result = {
        "episode_count": len(df),
        "event_count": int(df["event_observed"].sum()),
        "artifact_path": str(Path(artifact_path).resolve()),
        "concordance_index": float(cph.concordance_index_),
    }
    logger.info("Training hoàn tất: %s", result)
    return result


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train Cox PH model từ ml.machine_survival_episodes.")
    parser.add_argument("--artifact-path", type=str, default=DEFAULT_ARTIFACT_PATH)
    parser.add_argument("--penalizer", type=float, default=0.1)
    parser.add_argument("--no-cv", action="store_true", help="Bỏ qua 5-fold cross-validation (train nhanh hơn).")
    parser.add_argument("--min-events", type=int, default=DEFAULT_MIN_EVENTS)
    return parser.parse_args()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    args = _parse_args()
    output = run_training(
        artifact_path=args.artifact_path,
        penalizer=args.penalizer,
        run_cv=not args.no_cv,
        min_events=args.min_events,
    )
    print(output)