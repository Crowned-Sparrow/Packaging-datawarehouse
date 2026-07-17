CREATE TABLE IF NOT EXISTS Corrugating.fact_production_supply_usages (
    production_log_id  INT NOT NULL,
    supply_detail_id   INT NOT NULL,
    quantity_used      FLOAT NOT NULL CHECK (quantity_used > 0),
    PRIMARY KEY (production_log_id, supply_detail_id)
);