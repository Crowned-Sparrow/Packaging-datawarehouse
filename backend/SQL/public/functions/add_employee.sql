CREATE OR REPLACE FUNCTION add_employee(
    p_employee_name   VARCHAR(100),
    p_title           VARCHAR(50),
    p_contact_email   VARCHAR(50),
    p_contact_phone   VARCHAR(20),
    p_hash_password   VARCHAR(50)
)
RETURNS INT AS $$
DECLARE
    new_employee_id INT;
BEGIN
    INSERT INTO dim_employees (employee_name, title, contact_email, contact_phone, hash_password)
    VALUES (p_employee_name, p_title, p_contact_email, p_contact_phone, p_hash_password)
    RETURNING employee_id INTO new_employee_id;

    RETURN new_employee_id;
END;
$$ LANGUAGE plpgsql;