# app/models/product.py
from sqlalchemy import Column, Integer, DECIMAL, String, ForeignKey
from sqlalchemy.orm import relationship, declared_attr

from app.core.database import Base

class Product(Base):
    __abstract__ = True
    product_id = Column(Integer, primarykey = True)
    pds = Column(String(20),ForeignKey("fact_orders.pds"))
    @declared_attr
    def leader(cls):
        return relationship("Order", foreign_keys=[cls.pds])
    
class CorrugatingProduct(Product):
    length= Column(DECIMAL(10,2))
    width = Column(DECIMAL(10,2))
    unit = Column(String(20))