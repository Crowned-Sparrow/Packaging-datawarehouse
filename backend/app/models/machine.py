from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class Machine(Base):
    __abstract__ = True

    machine_id        = Column(Integer, primary_key=True, autoincrement=True)
    machine_name      = Column(String(100), nullable=False)
    lead_operator_id  = Column(Integer, ForeignKey("dim_employees.employee_id"), nullable=False)
    machine_status    = Column(String(20), nullable=False)

    lead_operator = relationship("Operator", back_populates="machines")

    __table_args__ = (
        CheckConstraint(
            "machine_status IN ('active', 'inactive', 'maintenance')",
            name="CK_machine_status",
        ),
    )

    def __repr__(self):
        return f"<Machine id={self.machine_id} name={self.machine_name} status={self.machine_status} operator={self.lead_operator_id}>"


class CorrugatingMachine(Machine):
    __tablename__ = "dim_machines"
    __table_args__ = (
        CheckConstraint("flute_type IN ('A','B','C','E','F')", name="CK_flute_type"),
        {"schema": "Corrugating"},
    )

    machine_id = Column(Integer, primary_key=True)
    flute_type = Column(String(20), nullable=False)
