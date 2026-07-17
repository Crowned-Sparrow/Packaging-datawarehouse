CREATE TABLE IF NOT EXISTS dim_employees(
    employee_id         SERIAL PRIMARY KEY,
    employee_name       VARCHAR(100) NOT NULL UNIQUE,
    title               VARCHAR(50) NOT NULL,
    contact_email       VARCHAR(50) NOT NULL,
    contact_phone       VARCHAR(20) NOT NULL,
    hash_password       VARCHAR(50) NOT NULL
);