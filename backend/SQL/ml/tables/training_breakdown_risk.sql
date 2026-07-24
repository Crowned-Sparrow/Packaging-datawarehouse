CREATE TABLE IF NOT EXISTS ml.training_breakdown_risk (
    feature_id BIGSERIAL PRIMARY KEY,
    
    feature_date DATE NOT NULL,
    machine_id INT NOT NULL,
    
    -- Metrics: production performance
    total_runs INT NOT NULL CHECK (total_runs >= 0),
    total_production_minutes NUMERIC(12, 2) NOT NULL CHECK (total_production_minutes >= 0),
    avg_run_minutes NUMERIC(8, 2) NOT NULL CHECK (avg_run_minutes >= 0),
    
    -- Metrics: breakdown frequency & duration
    breakdown_count INT NOT NULL CHECK (breakdown_count >= 0),
    downtime_minutes NUMERIC(12, 2) NOT NULL CHECK (downtime_minutes >= 0),
    
    -- Target label for ML
    label_has_breakdown INT NOT NULL CHECK (label_has_breakdown IN (0, 1)),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE (feature_date, machine_id),
    CONSTRAINT fk_machine_id FOREIGN KEY (machine_id) REFERENCES corrugating.dim_machines(machine_id) ON DELETE CASCADE
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_training_breakdown_risk_feature_date 
    ON ml.training_breakdown_risk(feature_date DESC);

CREATE INDEX IF NOT EXISTS idx_training_breakdown_risk_machine_id 
    ON ml.training_breakdown_risk(machine_id);

CREATE INDEX IF NOT EXISTS idx_training_breakdown_risk_label 
    ON ml.training_breakdown_risk(label_has_breakdown);

CREATE INDEX IF NOT EXISTS idx_training_breakdown_risk_date_machine 
    ON ml.training_breakdown_risk(feature_date DESC, machine_id);

-- Trigger to update updated_at on change
CREATE OR REPLACE FUNCTION ml.update_training_breakdown_risk_timestamp()
RETURNS TRIGGER AS $body$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$body$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_update_training_breakdown_risk_timestamp 
    ON ml.training_breakdown_risk;

CREATE TRIGGER trg_update_training_breakdown_risk_timestamp
BEFORE UPDATE ON ml.training_breakdown_risk
FOR EACH ROW
EXECUTE FUNCTION ml.update_training_breakdown_risk_timestamp();

COMMENT ON TABLE ml.training_breakdown_risk IS 
    'Daily aggregated machine features and breakdown prediction target labels for ML training.';

COMMENT ON COLUMN ml.training_breakdown_risk.feature_date IS 
    'Date for which features are computed (daily grain).';

COMMENT ON COLUMN ml.training_breakdown_risk.machine_id IS 
    'Reference to corrugating machine.';

COMMENT ON COLUMN ml.training_breakdown_risk.total_runs IS 
    'Total number of production runs on this machine for the day.';

COMMENT ON COLUMN ml.training_breakdown_risk.total_production_minutes IS 
    'Total production time in minutes for the day.';

COMMENT ON COLUMN ml.training_breakdown_risk.avg_run_minutes IS 
    'Average duration per run in minutes.';

COMMENT ON COLUMN ml.training_breakdown_risk.breakdown_count IS 
    'Number of machine breakdown incidents on this day.';

COMMENT ON COLUMN ml.training_breakdown_risk.downtime_minutes IS 
    'Total downtime in minutes caused by breakdowns.';

COMMENT ON COLUMN ml.training_breakdown_risk.label_has_breakdown IS 
    'Binary target label: 1 if machine had breakdown on feature_date, 0 otherwise. Used for classification.';
