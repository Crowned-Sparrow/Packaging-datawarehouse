# app/models/breakdown_log.py
from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint, DateTime, Text
from sqlalchemy.orm import relationship, declared_attr
from app.core.database import Base


class BreakDownLog(Base):
    __abstract__ = True

    breakdown_log_id = Column(Integer, primary_key=True,autoincrement=True)
    pds = Column(String(20), ForeignKey("fact_orders.pds"), nullable=False)
    supervisor_id = Column(Integer, ForeignKey("dim_employees.employee_id"), nullable=False)

    @declared_attr
    def supervisor(cls):
        return relationship("Employee", foreign_keys=[cls.supervisor_id])

    breakdown_time = Column(DateTime, nullable=False)
    recovery_time = Column(DateTime)
    breakdown_note = Column(Text)

    __table_args__ = (
        CheckConstraint("recovery_time >= breakdown_time", name="CK_time"),
    )


class CorrugatingBreakDownLog(BreakDownLog):
    __tablename__ = "fact_machine_breakdown_logs"

    machine_id = Column(Integer, ForeignKey("corrugating.dim_machines.machine_id"), nullable=False)
    breakdown_code = Column(Integer, ForeignKey("corrugating.dim_machine_breakdowns.breakdown_code"), nullable=False)

    machine = relationship("CorrugatingMachine")
    code = relationship("BreakDownCode", back_populates="machineBreakDownLog")

    __table_args__ = BreakDownLog.__table_args__ + (
        {"schema": "corrugating"},
    )

    def __repr__(self):
        return (
            f"<CorrugatingBreakDownLog id={self.breakdown_log_id} machine_id={self.machine_id} "
            f"code={self.breakdown_code} pds={self.pds!r} breakdown_time={self.breakdown_time!r} "
            f"recovery_time={self.recovery_time!r}>"
        )