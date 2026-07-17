CREATE OR REPLACE FUNCTION update_order_status()
RETURNS TRIGGER AS $$
BEGIN
    -- 1. Nếu cập nhật trạng thái thành 'cancelled' (Ưu tiên kiểm tra trước để tránh bị nhánh khác ghi đè)
    IF (TG_OP = 'UPDATE' AND NEW.order_status = 'cancelled' AND (OLD.order_status IS DISTINCT FROM 'cancelled')) THEN
        NEW.order_status := 'cancelled';

    -- 2. Nếu là INSERT, đặt trạng thái mặc định cho khách mới đặt hàng
    ELSIF (TG_OP = 'INSERT') THEN
        NEW.order_status := 'pending';

    -- 3. Nếu cập nhật ngày giao hàng (chuyển sang delivered)
    ELSIF (TG_OP = 'UPDATE' AND NEW.delivery_date IS NOT NULL AND OLD.delivery_date IS NULL) THEN
        NEW.order_status := 'delivered';

    -- 4. Nếu bắt đầu sản xuất (pds thay đổi từ NULL sang có giá trị)
    ELSIF (TG_OP = 'UPDATE' AND OLD.pds IS NULL AND NEW.pds IS NOT NULL) THEN
        NEW.order_status := 'in_progress';
    END IF;

    -- Bắt buộc phải return NEW trong trigger BEFORE INSERT/UPDATE
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;