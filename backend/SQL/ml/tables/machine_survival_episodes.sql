CREATE TABLE IF NOT EXISTS ml.machine_survival_episodes (
    episode_id      BIGSERIAL PRIMARY KEY,
    machine_id      INT NOT NULL REFERENCES corrugating.dim_machines(machine_id),
    episode_start   TIMESTAMP NOT NULL,
    episode_end     TIMESTAMP NOT NULL,  -- thời điểm hỏng, hoặc "hôm nay" nếu censored
    duration_days   NUMERIC(10,2) NOT NULL CHECK (duration_days > 0),
    event_observed  INT NOT NULL CHECK (event_observed IN (0,1)),  -- 1=hỏng, 0=censored
    flute_type      VARCHAR(20),
    machine_age_days INT,
    avg_utilization  NUMERIC(5,2),      -- static: trung bình cả episode (bản MVP)
    avg_waste_ratio  NUMERIC(5,2),
    total_runs       INT,
    prior_breakdown_count INT           -- số lần hỏng trước episode này (lịch sử)
);