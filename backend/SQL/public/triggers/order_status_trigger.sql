-- Trigger cho bảng fact_orders
DROP TRIGGER IF EXISTS trg_update_order_status_on ON fact_orders;

CREATE TRIGGER trg_update_order_status_on
BEFORE INSERT OR UPDATE ON fact_orders
FOR EACH ROW
EXECUTE FUNCTION update_order_status();
