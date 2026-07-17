CREATE TABLE IF NOT EXISTS Corrugating.fact_machine_breakdown_logs(
    breakdown_log_id       SERIAL PRIMARY KEY,
    machine_id             INT NOT NULL,
    supervisor_id           INT NOT NULL,
    breakdown_code         INT NOT NULL,
    pds                     VARCHAR(20) NOT NULL,
    breakdown_time          TIMESTAMP NOT NULL,
    recovery_time           TIMESTAMP,
    breakdown_note          TEXT
);