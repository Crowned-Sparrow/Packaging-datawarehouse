CREATE SCHEMA IF NOT EXISTS Corrugating ;
CREATE OR REPLACE PROCEDURE sp_init_corrygating_tables()
LANGUAGE plpgsql AS $$
BEGIN
-- Corrugating Process Tables

CREATE TABLE IF NOT EXISTS Corrugating.dim_machines(
    machine_id          SERIAL PRIMARY KEY,
    machine_name        VARCHAR(100) NOT NULL UNIQUE,
    flute_type          VARCHAR(20)  CHECK (flute_type IN ('A', 'B', 'C', 'E', 'F')),
    lead_operator_id    INT,
    machine_status      VARCHAR(20) CHECK (machine_status IN ('active', 'inactive', 'maintenance')) NOT NULL DEFAULT 'active',
    FOREIGN KEY (lead_operator_id) REFERENCES dim_employees(employee_id)
);

CREATE TABLE IF NOT EXISTS Corrugating.fact_production_logs(
    production_log_id    SERIAL PRIMARY KEY,
    -- mã sản xuất
    pds                  VARCHAR(20) UNIQUE NOT NULL,
    -- Thiết bị và nhân sự
    machine_id           INT NOT NULL,
    suplly_header_id     INT NOT NULL,
    product_id           INT NOT NULL,
    leader_id            INT NOT NULL,
    manager_id           INT NOT NULL,
    operator_id          INT NOT NULL,
    supervisor_id        INT NOT NULL,
    -- TIME
    start_time           TIMESTAMP NOT NULL,
    end_time             TIMESTAMP NOT NULL,
    -- Sản lượng và trọng lượng
    product_weight       FLOAT NOT NULL CHECK (product_weight > 0),
    material_weight      FLOAT NOT NULL CHECK (material_weight > 0),
    cut_pallet_count     INT NOT NULL CHECK (cut_pallet_count >= 0),
    -- Phế liệu
    waste_endroll_weight        FLOAT NOT NULL CHECK (waste_endroll_weight >= 0),
    waste_trim_weight           FLOAT NOT NULL CHECK (waste_trim_weight >= 0),
    waste_production_weight     FLOAT NOT NULL CHECK (waste_production_weight >= 0),
    waste_core_weight           FLOAT NOT NULL CHECK (waste_core_weight >= 0),
    returned_material_weight    FLOAT NOT NULL CHECK (returned_material_weight >= 0),
    -- Ghi chú
    log_note            TEXT,
    -- Ràng buộc khóa ngoại
    FOREIGN KEY (machine_id) REFERENCES Corrugating.dim_machines(machine_id),
    FOREIGN KEY (suplly_header_id) REFERENCES dim_suplly_headers(suplly_header_id),
    FOREIGN KEY (product_id) REFERENCES dim_products(product_id),
    FOREIGN KEY (leader_id) REFERENCES dim_employees(employee_id),
    FOREIGN KEY (manager_id) REFERENCES dim_employees(employee_id),
    FOREIGN KEY (operator_id) REFERENCES dim_employees(employee_id),
    FOREIGN KEY (supervisor_id) REFERENCES dim_employees(employee_id),
    FOREIGN KEY (pds) REFERENCES dim_orders(pds)    
);

-- Machine breakdown table
CREATE TABLE IF NOT EXISTS Corrugating.dim_machine_breakdowns(
    breakdown_code         SERIAL PRIMARY KEY,
    description              TEXT NOT NULL,
    how_to_handle             TEXT NOT NULL,
    -- this field is used by model to predict expected downtime, so it should be non-negative
    expected_downtime_minutes INT CHECK (expected_downtime_minutes >= 0)
);

CREATE TABLE IF NOT EXISTS Corrugating.fact_machine_breakdown_logs(
    breakdown_log_id       SERIAL PRIMARY KEY,
    machine_id             INT NOT NULL,
    supervisor_id           INT NOT NULL,
    breakdown_code         INT NOT NULL,
    pds                     VARCHAR(20) NOT NULL,
    breakdown_time          TIMESTAMP NOT NULL,
    recovery_time           TIMESTAMP,
    breakdown_note          TEXT,
    -- Ràng buộc khóa ngoại
    FOREIGN KEY (machine_id) REFERENCES Corrugating.dim_machines(machine_id),
    FOREIGN KEY (supervisor_id) REFERENCES dim_employees(employee_id),
    FOREIGN KEY (breakdown_code) REFERENCES Corrugating.dim_machine_breakdowns(breakdown_code),
    FOREIGN KEY (pds) REFERENCES dim_orders(pds)    

);
END;
$$;