CREATE TABLE IF NOT EXISTS fact_supply_details(
    supply_detail_id    SERIAL PRIMARY KEY,
    supplier_id         INT NOT NULL, --FK
    material_id         INT NOT NULL, --FK
    quantity            NUMERIC(10,2) NOT NULL CHECK (quantity > 0),
    unit_price          NUMERIC(10,2) NOT NULL CHECK (unit_price >= 0),
    request_date        DATE NOT NULL,
    receive_date        DATE ,    CHECK (receive_date >= request_date)

);