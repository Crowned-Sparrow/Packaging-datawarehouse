CREATE TABLE IF NOT EXISTS Corrugating.fact_production_logs(
    production_log_id    SERIAL PRIMARY KEY,
    -- mã sản xuất
    pds                  VARCHAR(20) UNIQUE NOT NULL,
    -- Thiết bị và nhân sự
    machine_id           INT NOT NULL,

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
    log_note            TEXT
);