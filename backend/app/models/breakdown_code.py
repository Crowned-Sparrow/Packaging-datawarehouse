from sqlalchemy import Column, Integer, Text, CheckConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base

class BreakDownCode(Base):
    __tablename__ = "dim_machine_breakdowns"
    __table_args__ = (
        CheckConstraint(
            "expected_downtime_minutes >= 0",
            name="CK_downtime",
        ),
        {"schema": "corrugating"},
    )

    breakdown_code = Column(Integer, primary_key=True)
    description = Column(Text, nullable=False)
    how_to_handle = Column(Text)
    expected_downtime_minutes = Column(Integer)

    machineBreakDownLog = relationship("MachineBreakDownLog", back_populates="code")

    def __repr__(self):
        return f"<BreakDownCode code={self.breakdown_code} description={self.description!r}>"
