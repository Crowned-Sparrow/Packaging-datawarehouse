from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class MachineBreakdownLogCreate(BaseModel):
    machine_id: int
    supervisor_id: int
    breakdown_code:int
    pds:str
    breakdown_time: datetime
    breakdown_note: Optional[str]

class MachineBreakDownLogOut(BaseModel):
    breakdown_log_id: int
    machine_id: int
    supervisor_id: int
    breakdown_code:int
    ##pds:str ẩn thông số production sheet code
    breakdown_time: datetime
    recovery_time: Optional[datetime]
    breakdown_note: Optional[str]

    class Config:
        from_attributes = True

class UpdateMachineBreakDownLog(BaseModel):
    recovery_time:datetime
    breakdown_note: Optional[str]