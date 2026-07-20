from pydantic import BaseModel
from typing import Literal

class MachineBase(BaseModel):
    machine_name:str
    lead_operator_id:int

class MachineCreate(MachineBase):
    pass
    
class MachineOut(BaseModel):
    machine_id: int
    machine_status:str

    class Config:
        from_attributes = True

class MachineUpdateStatus(BaseModel):
    machine_status: Literal['active', 'inactive', 'maintenance']

class CorrugatingMachineCreate(MachineCreate):
    flute_type: Literal['A', 'B', 'C', 'E', 'F']

class CorrugatingMachineOut(MachineOut):
    flute_type:str
