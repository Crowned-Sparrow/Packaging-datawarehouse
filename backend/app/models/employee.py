# app/models/employee.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Employee(Base):
    __tablename__ = "dim_employees"

    employee_id     = Column(Integer, primary_key=True, autoincrement=True)
    employee_name   = Column(String(100), nullable=False, unique=True)
    title           = Column(String(50), nullable=False)
    contact_email   = Column(String(50), nullable=False)
    contact_phone   = Column(String(20), nullable=False)
    hash_password   = Column(String(50), nullable=False)

    def __repr__(self):
        return f"<Employee id={self.employee_id} name={self.employee_name!r}>"