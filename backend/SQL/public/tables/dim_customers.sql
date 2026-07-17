CREATE TABLE IF NOT EXISTS dim_customers(
    customer_id         SERIAL PRIMARY KEY,
    customer_name       VARCHAR(100) NOT NULL,
    contact_phone       VARCHAR(20) NOT NULL,
    contact_email       VARCHAR(50) NOT NULL
);