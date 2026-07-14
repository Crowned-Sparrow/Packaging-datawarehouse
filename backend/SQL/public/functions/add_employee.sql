CREATE OR REPLACE FUNCTION add_employee(
    p_employee_name       VARCHAR(100),
    p_title               VARCHAR(50),
    p_contact_email       VARCHAR(50),
    p_contact_phone       VARCHAR(20)
)
RETURNS INT AS $$
DECLARE
    new_employee_id INT;
BEGIN
    INSERT INTO dim_employees (employee_name, title, contact_email, contact_phone)
    VALUES (p_employee_name, p_title, p_contact_email, p_contact_phone)
    RETURNING employee_id INTO new_employee_id;
    
    RETURN new_employee_id;
END;
$$ LANGUAGE plpgsql;

SELECT add_employee(
    p_employee_name := 'Jane Smith',
    p_title := 'Project Manager',
    p_contact_email := 'jane.smith@email.com',
    p_contact_phone := '555-0144'
);