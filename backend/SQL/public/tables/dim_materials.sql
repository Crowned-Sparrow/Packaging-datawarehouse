CREATE TABLE IF NOT EXISTS dim_materials(
    material_id         SERIAL PRIMARY KEY,
    material_code       VARCHAR(50) NOT NULL UNIQUE,
    material_name       VARCHAR(100) NOT NULL,
    material_type       VARCHAR(50) NOT NULL CHECK (material_type IN ('paper', 'ink', 'glue', 'other')),
    unit                VARCHAR(20) NOT NULL CHECK (unit IN ('kg', 'liter', 'sheet', 'roll', 'other'))
    );