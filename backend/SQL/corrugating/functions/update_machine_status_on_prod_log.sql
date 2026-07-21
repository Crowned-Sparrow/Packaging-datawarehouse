-- Hàm cập nhật trạng thái từ log sản xuất
CREATE OR REPLACE FUNCTION corrugating.update_machine_status_on_production_log()
RETURNS TRIGGER AS $$
BEGIN
    -- Tính toán lại trạng thái dựa trên toàn bộ dữ liệu thực tế hiện tại
    UPDATE corrugating.dim_machines 
    SET machine_status = corrugating.get_current_machine_status(NEW.machine_id) 
    WHERE machine_id = NEW.machine_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;