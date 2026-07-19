CREATE TABLE IF NOT EXISTS dim_suppliers(
    supplier_id         SERIAL PRIMARY KEY,
    supplier_name       VARCHAR(100) NOT NULL,
    contact_email       VARCHAR(50) NOT NULL,
    contact_phone        VARCHAR(20) NOT NULL
);