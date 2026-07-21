CREATE TABLE IF NOT EXISTS corrugating.fact_products(
    product_id      INT PRIMARY KEY,
    length          DECIMAL(10,2),
    width           DECIMAL(10,2),
    unit            VARCHAR(20) DEFAULT('mm'),
    pds             VARCHAR(20) UNIQUE
);