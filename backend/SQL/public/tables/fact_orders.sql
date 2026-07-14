CREATE TABLE IF NOT EXISTS fact_orders(
    order_id            SERIAL PRIMARY KEY,
    -- Production Data Sheet code, dùng để liên kết với bảng production logs
    -- Chỉ được cập nhật sau khi chấp nhận đơn hàng
    pds                 VARCHAR(20) UNIQUE, 

    customer_id         INT NOT NULL, --FK
    order_date          DATE NOT NULL,
    -- Ngày giao hàng được cập nhật sau
    delivery_date       DATE ,
    
    quantity            INT NOT NULL CHECK (quantity > 0),
    order_note          TEXT,
    order_status        VARCHAR(20) CHECK (order_status IN ('pending', 'in_progress', 'delivered', 'cancelled')) NOT NULL DEFAULT 'pending'
);