ALTER TABLE Corrugating.dim_machines
    ADD CONSTRAINT FK_Co_machine_employee
        FOREIGN KEY (lead_operator_id)
        REFERENCES dim_employees(employee_id);

ALTER TABLE Corrugating.fact_machine_breakdown_logs
    ADD CONSTRAINT FK_Co_machine_breakdown_machine
        FOREIGN KEY (machine_id)
        REFERENCES Corrugating.dim_machines(machine_id),
    ADD CONSTRAINT FK_Co_machine_breakdown_supervisor
        FOREIGN KEY (supervisor_id)
        REFERENCES dim_employees(employee_id),
    ADD CONSTRAINT FK_Co_machine_breakdown_code
        FOREIGN KEY (breakdown_code)
        REFERENCES Corrugating.dim_machine_breakdowns(breakdown_code),
    ADD CONSTRAINT FK_Co_machine_breakdown_order
        FOREIGN KEY (pds)
        REFERENCES fact_orders(pds);

ALTER TABLE Corrugating.fact_production_supply_usages
    ADD CONSTRAINT FK_Co_production_usage_log
        FOREIGN KEY (production_log_id)
        REFERENCES Corrugating.fact_production_logs(production_log_id),
    ADD CONSTRAINT FK_Co_production_usage_supply_detail
        FOREIGN KEY (supply_detail_id)
        REFERENCES fact_supply_details(supply_detail_id);

ALTER TABLE Corrugating.fact_products
    ADD CONSTRAINT FK_Co_product_pds
        FOREIGN KEY (pds)
        REFERENCES fact_orders(pds);

ALTER TABLE Corrugating.fact_production_logs
    ADD CONSTRAINT FK_Co_production_log_machine
        FOREIGN KEY (machine_id)
        REFERENCES Corrugating.dim_machines(machine_id),
    ADD CONSTRAINT FK_Co_production_product
        FOREIGN KEY (product_id)
        REFERENCES Corrugating.fact_products(product_id),
    ADD CONSTRAINT FK_Co_production_leader
        FOREIGN KEY (leader_id)
        REFERENCES dim_employees(employee_id),
    ADD CONSTRAINT FK_Co_production_manager
        FOREIGN KEY (manager_id)
        REFERENCES dim_employees(employee_id),
    ADD CONSTRAINT FK_Co_production_operator
        FOREIGN KEY (operator_id)
        REFERENCES dim_employees(employee_id),
    ADD CONSTRAINT FK_Co_production_supervisor
        FOREIGN KEY (supervisor_id)
        REFERENCES dim_employees(employee_id),
    ADD CONSTRAINT FK_Co_production_log_pds
        FOREIGN KEY (pds)
        REFERENCES fact_orders(pds);
