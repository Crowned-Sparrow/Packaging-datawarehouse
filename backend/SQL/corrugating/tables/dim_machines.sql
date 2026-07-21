CREATE TABLE IF NOT EXISTS corrugating.dim_machines(
    machine_id          SERIAL PRIMARY KEY,
    machine_name        VARCHAR(100) NOT NULL UNIQUE,
    flute_type          VARCHAR(20)  CHECK (flute_type IN ('A', 'B', 'C', 'E', 'F')),
    lead_operator_id    INT,
    machine_status      VARCHAR(20) CHECK (machine_status IN ('active', 'inactive', 'maintenance')) NOT NULL DEFAULT 'active'
    --FOREIGN KEY (lead_operator_id) REFERENCES dim_employees(employee_id)
);