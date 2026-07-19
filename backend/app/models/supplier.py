# app/models/customer.py
from sqlalchemy import Column, Integer, String
from app.core.database import Base


class Supplier(Base):
    __tablename__ = "dim_suppliers"

    supplier_id     = Column(Integer, primary_key=True, autoincrement=True)
    supplier_name   = Column(String(100), nullable=False)
    contact_phone   = Column(String(20), nullable=False)
    contact_email   = Column(String(50), nullable=False)

    def __repr__(self):
        return f"<Supplier id={self.supplier_id} name={self.supplier_name!r} email={self.contact_email!r} phone={self.contact_phone!r}>"