CREATE OR REPLACE FUNCTION corrugating.get_current_machine_status(p_machine_id INT)
RETURNS VARCHAR AS $$
DECLARE
    v_status VARCHAR;
BEGIN
    -- 1. Kiểm tra xem máy có đang bị sự cố chưa khắc phục không
    IF EXISTS (
        SELECT 1 FROM corrugating.fact_machine_breakdown_logs 
        WHERE machine_id = p_machine_id AND recovery_time IS NULL
    ) THEN 
        RETURN 'maintenance';
        
    -- 2. Kiểm tra xem máy có đang trong ca sản xuất chưa kết thúc không
    ELSIF EXISTS (
        SELECT 1 FROM corrugating.fact_production_logs 
        WHERE machine_id = p_machine_id AND end_time IS NULL
    ) THEN 
        RETURN 'active';
        
    -- 3. Nếu không thuộc 2 trường hợp trên thì máy đang rảnh
    ELSE 
        RETURN 'inactive';
    END IF;
END;
$$ LANGUAGE plpgsql;