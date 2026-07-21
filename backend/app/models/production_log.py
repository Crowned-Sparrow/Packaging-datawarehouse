from sqlalchemy import Column, DECIMAL, Integer, String, ForeignKey, CheckConstraint, DateTime, Text
from app.core.database import Base
from sqlalchemy.orm import relationship


class ProductionLog(Base):
    __abstract__ = True

    production_log_id = Column(Integer, primary_key=True)
    pds = Column(String(20), ForeignKey("fact_orders.pds"), nullable=False)

    leader_id     = Column(Integer, ForeignKey("dim_employees.employee_id"), nullable=False)
    manager_id    = Column(Integer, ForeignKey("dim_employees.employee_id"), nullable=False)
    operator_id   = Column(Integer, ForeignKey("dim_employees.employee_id"), nullable=False)
    supervisor_id = Column(Integer, ForeignKey("dim_employees.employee_id"), nullable=False)

    leader = relationship("Leader", back_populates="production_log")
    manager= relationship("Manger", back_populates= "production_log")
    operator= relationship("Operator", back_populates="production_log")
    supervisor = relationship("Supervisor", back_populates="production_log")

    start_time = Column(DateTime, nullable=False)
    end_time   = Column(DateTime)

    product_weight  = Column(DECIMAL(10, 2))
    material_weight = Column(DECIMAL(10, 2))

    log_note = Column(Text)

    __table_args__ = (
        CheckConstraint("product_weight > 0", name="CK_product_weight"),
        CheckConstraint("end_time >= start_time", name="CK_time"),
    )


class CorrugatingProductionLog(ProductionLog):
    __tablename__ = "fact_production_logs"

    machine_id = Column(Integer, ForeignKey("corrugating.dim_machines.machine_id"), nullable=False)
    product_id = Column(Integer, ForeignKey("corrugating.fact_products.product_id"), nullable=False)
    
    machine = relationship("Machine",back_populates="production_log")
    product = relationship("Product", back_populates="production_log")

    cut_pallet_count         = Column(Integer)
    waste_endroll_weight     = Column(DECIMAL(10, 2))
    waste_trim_weight        = Column(DECIMAL(10, 2))
    waste_production_weight  = Column(DECIMAL(10, 2))
    waste_core_weight        = Column(DECIMAL(10, 2))

    __table_args__ = ProductionLog.__table_args__ + (
        CheckConstraint("cut_pallet_count > 0", name="CK_cut_pallet_count"),
        CheckConstraint("waste_endroll_weight > 0", name="CK_waste_endroll_weight"),
        CheckConstraint("waste_trim_weight > 0", name="CK_waste_trim_weight"),
        CheckConstraint("waste_production_weight > 0", name="CK_waste_production_weight"),
        CheckConstraint("waste_core_weight > 0", name="CK_waste_core_weight"),
        {"schema": "corrugating"},
    )