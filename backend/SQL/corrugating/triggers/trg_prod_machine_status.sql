CREATE TRIGGER trg_prod_machine_status
AFTER INSERT OR UPDATE ON Corrugating.fact_production_logs
FOR EACH ROW EXECUTE FUNCTION Corrugating.update_machine_status_on_production_log();