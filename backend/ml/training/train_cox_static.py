# backend/ml/training/train_cox_static.py
from __future__ import annotations

import logging
from pathlib import Path

import joblib
import pandas as pd
from lifelines import CoxPHFitter
from lifelines.utils import k_fold_cross_validation

logger = logging.getLogger(__name__)
## **NOTE**: Tạm tắt 1 số feauture
FEATURE_COLS = [
    "machine_age_days",
    "prior_breakdown_count",
    #"lifetime_avg_downtime_minutes", nếu có data thật không phải tự tạo ngẫu nhiên thì bật feature này
    "runs_30d",
    "utilization_30d",
    "waste_ratio_30d",
    "breakdown_count_90d",
]
CATEGORICAL_COLS = ["flute_type"]

# machine_id không phải feature dự đoán (không nằm trong FEATURE_COLS, không
# đưa vào model để fit hệ số), mà chỉ dùng để GOM NHÓM (cluster) các episode
# thuộc cùng 1 máy khi tính standard error. Nhiều episode liên tiếp từ cùng
# một máy vốn không hoàn toàn độc lập với nhau (đặc điểm riêng của máy đó lặp
# lại qua từng episode) — vi phạm nhẹ giả định "independent observations" của
# Cox model. Cluster theo machine_id giúp standard error phản ánh đúng hơn
# mức độ không chắc chắn thật của hệ số ước lượng (thường sẽ RỘNG hơn so với
# không cluster, tức model sẽ "khiêm tốn" hơn về mức độ tin cậy).
CLUSTER_COL = "machine_id"

REQUIRED_COLS = FEATURE_COLS + CATEGORICAL_COLS + [CLUSTER_COL, "duration_days", "event_observed"]


def encode_features(df: pd.DataFrame, dummy_cols: list[str] | None = None) -> pd.DataFrame:
    """
    Encode categorical -> dummy, ép kiểu numeric.
    Dùng chung cho cả train và serving để tránh lệch cột.

    - Lúc train: gọi không truyền dummy_cols, hàm tự phát hiện.
    - Lúc serving: truyền đúng dummy_cols đã lưu từ lúc train, để reindex
      (đảm bảo cùng số cột / cùng thứ tự dù input chỉ có 1 dòng).

    Lưu ý: CLUSTER_COL (machine_id) không bị đụng tới ở đây — nếu có mặt
    trong df đầu vào, nó được giữ nguyên qua hàm này (không phải dummy, không
    bị ép kiểu bool->int), vì nó không phải feature mà chỉ đi kèm để cluster
    lúc fit. Lúc serving (dummy_cols khác None), nếu machine_id không nằm
    trong dummy_cols thì việc reindex `encoded[dummy_cols]` ở dưới sẽ tự loại
    nó ra — đúng ý muốn, vì lúc serving không cần cluster.
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

    n_machines = df[CLUSTER_COL].nunique()
    if n_machines < 5:
        logger.warning(
            "Chỉ có %d máy (machine_id) trong dữ liệu — cluster-robust SE vẫn "
            "chạy được nhưng với quá ít cluster thì ước lượng SE dễ không ổn "
            "định. Kết quả nên được đọc thận trọng cho tới khi có nhiều máy hơn.",
            n_machines,
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
    # model_df giữ thêm CLUSTER_COL (machine_id) bên cạnh feature_cols +
    # duration/event — lifelines cần cột này có mặt trong df truyền vào fit()
    # để group theo cluster, nhưng nó KHÔNG nằm trong feature_cols nên không
    # được coi là biến dự đoán / không có hệ số riêng trong model.
    model_df = df_encoded[feature_cols + [CLUSTER_COL, "duration_days", "event_observed"]]
    print(">>> Đang fit với cluster_col =", CLUSTER_COL)

    cph = CoxPHFitter(penalizer=penalizer)
    cph.fit(
        model_df,
        duration_col="duration_days",
        event_col="event_observed",
        cluster_col=CLUSTER_COL,
    )

    cph.print_summary()  # hazard ratio + p-value từng feature (SE đã robust theo machine_id)

    # Kiểm tra giả định Proportional Hazards — bắt buộc phải làm với Cox.
    # Lưu ý: hàm này in cảnh báo ra console/log, không return bool, nên
    # cần đọc kỹ output khi chạy để biết feature nào vi phạm giả định.
    #
    # check_assumptions() của lifelines không hỗ trợ cluster_col, nên ở đây
    # ta kiểm tra trên model_df gốc (không cluster) — vẫn hợp lệ vì assumption
    # check quan tâm tới SHAPE của hazard theo thời gian, không phụ thuộc vào
    # cách tính SE.
    try:
        cph.check_assumptions(model_df, p_value_threshold=0.05, show_plots=False)
    except Exception as exc:  # lifelines có thể raise nếu vi phạm nghiêm trọng
        logger.warning("Giả định Proportional Hazards có thể bị vi phạm: %s", exc)

    if run_cv:
        # QUAN TRỌNG: k_fold_cross_validation tự fit 5 model MỚI trên từng fold,
        # KHÔNG phải đánh giá lại con `cph` đã fit ở trên. Đây là cách đánh giá
        # đúng (tránh leak), nhưng model được LƯU (joblib.dump bên dưới) là model
        # fit trên toàn bộ dữ liệu, không phải model của fold nào.
        #
        # fitter_kwargs được truyền thẳng vào .fit() của từng fold, nên cluster
        # theo machine_id cũng được áp dụng nhất quán trong CV.
        scores = k_fold_cross_validation(
            CoxPHFitter(penalizer=penalizer), model_df,
            duration_col="duration_days", event_col="event_observed",
            k=5, scoring_method="concordance_index",
            fitter_kwargs={"cluster_col": CLUSTER_COL},
        )
        logger.info("C-index (5-fold CV): %.3f ± %.3f", pd.Series(scores).mean(), pd.Series(scores).std())

    artifact_dir = Path(artifact_path).parent
    artifact_dir.mkdir(parents=True, exist_ok=True)

    joblib.dump(
        {
            "model": cph,
            "feature_cols": feature_cols,          # dùng để reindex lúc serving (KHÔNG gồm machine_id)
            "penalizer": penalizer,
        },
        artifact_path,
    )
    logger.info("Đã lưu model tại %s", artifact_path)

    return cph