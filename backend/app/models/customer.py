# app/models/customer.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.order import Order
from app.core.database import Base


class Customer(Base):
    __tablename__ = "dim_customers"

    customer_id     = Column(Integer, primary_key=True, autoincrement=True)
    customer_name   = Column(String(100), nullable=False)
    contact_phone   = Column(String(20), nullable=False)
    contact_email   = Column(String(50), nullable=False)

    orders = relationship("Order", back_populates="customer")

    def __repr__(self):
        return f"<Customer id={self.customer_id} name={self.customer_name!r} email={self.contact_email!r} phone={self.contact_phone!r}>"