from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint, DateTime, Text
from app.core.database import Base
from sqlalchemy.orm import relationship

class MachineBreakDownLog(Base):
    __tablename__ = "fact_machine_breakdown_logs"
    __table_args__ = (
        CheckConstraint(
            "recovery_time >= breakdown_time",
            name="CK_time",
        ),
        {"schema": "corrugating"},
    )

    breakdown_log_id = Column(Integer, primary_key=True)
    machine_id = Column(ForeignKey("corrugating.dim_machines.machine_id"), nullable=False)
    supervisor_id = Column(ForeignKey("dim_employees.employee_id"), nullable=False)
    breakdown_code = Column(ForeignKey("corrugating.dim_machine_breakdowns"), nullable=False)
    pds = Column(String(20), nullable=False)
    breakdown_time = Column(DateTime, nullable=False)
    recovery_time = Column(DateTime)
    breakdown_note = Column(Text)

    machine = relationship("Machine", back_populates="machineBreakDownLog")
    supervisor = relationship("Supervisor", back_populates="machineBreakDownLog")
    code = relationship("BreakdownCode", back_populates="machineBreakDownLog")

    def __repr__(self):
        return (
            f"<MachineBreakDownLog id={self.breakdown_log_id} machine_id={self.machine_id} "
            f"code={self.breakdown_code} pds={self.pds!r} breakdown_time={self.breakdown_time!r} "
            f"recovery_time={self.recovery_time!r}>"
        )