from sqlalchemy import Column, Integer, ForeignKey, DECIMAL, Date, CheckConstraint 
from sqlalchemy.orm import relationship 
from app.core.database import Base 

class SupplyDetail(Base): 
    __tablename__ = "fact_supply_detail" 
    
    supply_detail_id = Column(Integer, primary_key=True) 
    supplier_id = Column(Integer, ForeignKey("dim_suppliers.supplier_id"), nullable=False) 
    material_id = Column(Integer, ForeignKey("dim_materials.material_id"), nullable=False) 
    quantity = Column(Integer, nullable=False) 
    
    unit_price = Column(DECIMAL(10, 2), nullable=False) 
    
    request_date = Column(Date, nullable=False) 
    receive_date = Column(Date, nullable=False) 
    
    supplier = relationship("Supplier", back_populates="supply_details") 
    material = relationship("Material", back_populates="supply_details") 
    
    __table_args__ = ( 
        CheckConstraint( "quantity > 0", name="CK_supply_detail_quantity_positive" ), 
        CheckConstraint( "request_date <= receive_date", name="CK_supply_detail_date" ), 
    ) 
    
    def __repr__(self): 
        return f"<Supply detail id={self.supply_detail_id} supplier_id={self.supplier_id} quantity={self.quantity!r} unit_price={self.unit_price!r} request_date={self.request_date!r} receive_date={self.receive_date!r}>"
