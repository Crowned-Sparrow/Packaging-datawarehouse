-- Optional: Drop function if it exists (for re-runs)
DROP TRIGGER IF EXISTS trg_update_training_breakdown_risk_timestamp 
    ON ml.training_breakdown_risk;

DROP FUNCTION IF EXISTS ml.update_training_breakdown_risk_timestamp();
