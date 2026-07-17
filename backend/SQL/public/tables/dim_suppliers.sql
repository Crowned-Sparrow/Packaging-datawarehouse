CREATE TABLE IF NOT EXISTS dim_suppliers(
    supplier_id         SERIAL PRIMARY KEY,
    supplier_name       VARCHAR(100) NOT NULL UNIQUE,
    email               VARCHAR(50) NOT NULL,
    phone_number        VARCHAR(20)
);