-- Machine breakdown table
CREATE TABLE IF NOT EXISTS Corrugating.dim_machine_breakdowns(
    breakdown_code         SERIAL PRIMARY KEY,
    description              TEXT NOT NULL,
    how_to_handle             TEXT NOT NULL,
    -- this field is used by model to predict expected downtime, so it should be non-negative
    expected_downtime_minutes INT CHECK (expected_downtime_minutes >= 0)
);