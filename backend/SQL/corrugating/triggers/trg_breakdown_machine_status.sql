-- Trigger cho bảng fact_machine_breakdown_logs
CREATE TRIGGER trg_breakdown_machine_status
AFTER INSERT OR UPDATE ON corrugating.fact_machine_breakdown_logs
FOR EACH ROW EXECUTE FUNCTION corrugating.update_machine_status_on_breakdown();