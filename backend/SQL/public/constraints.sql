ALTER TABLE fact_orders
    ADD CONSTRAINT FK_order_customer
        FOREIGN KEY (customer_id)
        REFERENCES dim_customers(customer_id);

ALTER TABLE fact_supply_details
    ADD CONSTRAINT FK_supply_detail_supplier
        FOREIGN KEY (supplier_id)
        REFERENCES dim_suppliers(supplier_id),
    ADD CONSTRAINT FK_supply_detail_material
        FOREIGN KEY (material_id)
        REFERENCES dim_materials(material_id);
