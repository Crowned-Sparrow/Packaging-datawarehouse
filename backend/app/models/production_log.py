from sqlalchemy import Column,DECIMAL,Integer,String, ForeignKey, CheckConstraint, Date, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class ProductionLog(Base):
    __abstract__ = True

    prodcution_log_id = Column(Integer,primary_key= True)
    pds = Column(Integer,ForeignKey("dim_orders.pds"), nullable= False)

    leader_id = Column(Integer,ForeignKey("dim_employees.employee_id"), nullable=False)
    manager_id = Column(Integer,ForeignKey("dim_employees.employee_id", nullable = False))
    operator_id = Column(Integer,ForeignKey("dim_employees.employee_id", nullable = False))
    supervisor_id = Column(Integer,ForeignKey("dim_employees.employee_id", nullable = False))

    start_time = Column(Date,nullable= False)
    end_time = Column(Date)

    product_weight = Column(DECIMAL(10,2))
    material_weight = Column(DECIMAL(10,2))

    log_note = Column(Text)
    __table_args__= (
        CheckConstraint(
            "product_weight > 0",
            name= "CK_product_weight"
        ),
        CheckConstraint(
            "end_time >= start_time",
            name= "CK_time"
        ),
    )


class CorrugatingProductionLog(ProductionLog):
    machine_id = Column(Integer,ForeignKey("corrugating.machine_id"), nullable=False)
    product_id = Column(Integer,ForeignKey("corrugating.fact_products.product_id"), nullable=False)

    cut_pallet_count = Column(Integer)
    waste_endroll_weight = Column(DECIMAL(10,2))
    waste_trim_weight = Column(DECIMAL(10,2))
    waste_production_weight = Column(DECIMAL(10,2))
    waste_core_weight = Column(DECIMAL(10,2))
    __table_args__ = (
        CheckConstraint(
            "cut_pallet_count > 0",
            name= "CK_cut_pallet_count"
        ),
        CheckConstraint(
            "waste_endroll_weight > 0",
            name= "CK_waste_endroll_weight"
        ),
        CheckConstraint(
            "waste_trim_weight > 0",
            name= "CK_waste_trim_weight"
        ),
        CheckConstraint(
            "waste_production_weight > 0",
            name="CK_waste_production_weight"
        ),
        CheckConstraint(
            "waste_waste_core_weight > 0",
            name= "CK_waste_core_weight"
        ),
    )

    