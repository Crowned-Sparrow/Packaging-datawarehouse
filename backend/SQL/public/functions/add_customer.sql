CREATE OR REPLACE FUNCTION add_customer(
    p_customer_name       VARCHAR(100),
    p_contact_email       VARCHAR(50),
    p_contact_phone       VARCHAR(20)
)
RETURNS INT AS $$
DECLARE
    new_customer_id INT;
BEGIN
    INSERT INTO dim_customers (customer_name, contact_email, contact_phone)
    VALUES (p_customer_name, p_contact_email, p_contact_phone)
    RETURNING customer_id INTO new_customer_id;
    
    RETURN new_customer_id;
END;
$$ LANGUAGE plpgsql;

SELECT add_customer(
    p_customer_name:= 'NESTLE',
    p_contact_email:= 'nestle-company@gmail.com',
    p_contact_phone:= '555-0143'
);
