-- backend/SQL/ml/tables/machine_survival_episodes.sql
-- Schema khớp 1-1 với output của backend/ml/features/build_survival_episodes.py
-- Mỗi dòng = 1 episode (khoảng thời gian giữa 2 lần hỏng liên tiếp của 1 máy)

CREATE TABLE IF NOT EXISTS ml.machine_survival_episodes (
    episode_id      BIGSERIAL PRIMARY KEY,
    machine_id      INT NOT NULL REFERENCES corrugating.dim_machines(machine_id),

    episode_start   TIMESTAMP NOT NULL,
    episode_end     TIMESTAMP NOT NULL,   -- thời điểm hỏng, hoặc as_of_date nếu censored
    duration_days   NUMERIC(10,2) NOT NULL CHECK (duration_days > 0),
    event_observed  INT NOT NULL CHECK (event_observed IN (0,1)),  -- 1=hỏng, 0=censored
    --  Static / lifetime features (tính tại thời điểm episode_start, tránh leak) 
    flute_type                     VARCHAR(20),
    machine_age_days               NUMERIC(10,2),   -- NULL nếu chưa từng có log nào trước episode_start
    lifetime_total_runs            INT NOT NULL DEFAULT 0,
    lifetime_breakdown_count       INT NOT NULL DEFAULT 0,
    lifetime_avg_downtime_minutes  NUMERIC(10,2) NOT NULL DEFAULT 0,
    days_since_last_breakdown      NUMERIC(10,2),   -- NULL nếu máy chưa từng hỏng trước episode này
    prior_breakdown_count          INT NOT NULL DEFAULT 0,
    --  Rolling features — cửa sổ 7 ngày 
    runs_7d              INT NOT NULL DEFAULT 0,
    utilization_7d        NUMERIC(6,4) NOT NULL DEFAULT 0 CHECK (utilization_7d BETWEEN 0 AND 1),
    waste_ratio_7d         NUMERIC(8,4) NOT NULL DEFAULT 0,
    avg_cut_pallet_7d      NUMERIC(10,2) NOT NULL DEFAULT 0,
    breakdown_count_7d     INT NOT NULL DEFAULT 0,
    downtime_minutes_7d    NUMERIC(10,2) NOT NULL DEFAULT 0,
    --  Rolling features — cửa sổ 30 ngày 
    runs_30d              INT NOT NULL DEFAULT 0,
    utilization_30d        NUMERIC(6,4) NOT NULL DEFAULT 0 CHECK (utilization_30d BETWEEN 0 AND 1),
    waste_ratio_30d         NUMERIC(8,4) NOT NULL DEFAULT 0,
    avg_cut_pallet_30d      NUMERIC(10,2) NOT NULL DEFAULT 0,
    breakdown_count_30d     INT NOT NULL DEFAULT 0,
    downtime_minutes_30d    NUMERIC(10,2) NOT NULL DEFAULT 0,
    --  Rolling features — cửa sổ 90 ngày 
    runs_90d              INT NOT NULL DEFAULT 0,
    utilization_90d        NUMERIC(6,4) NOT NULL DEFAULT 0 CHECK (utilization_90d BETWEEN 0 AND 1),
    waste_ratio_90d         NUMERIC(8,4) NOT NULL DEFAULT 0,
    avg_cut_pallet_90d      NUMERIC(10,2) NOT NULL DEFAULT 0,
    breakdown_count_90d     INT NOT NULL DEFAULT 0,
    downtime_minutes_90d    NUMERIC(10,2) NOT NULL DEFAULT 0,

    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Index phục vụ truy vấn theo máy / lọc theo event_observed khi build training set
CREATE INDEX IF NOT EXISTS idx_survival_episodes_machine_id
    ON ml.machine_survival_episodes(machine_id);

CREATE INDEX IF NOT EXISTS idx_survival_episodes_event_observed
    ON ml.machine_survival_episodes(event_observed);