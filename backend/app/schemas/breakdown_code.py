from typing import Optional
from pydantic import BaseModel

class BreakDownCodeCreate(BaseModel):
    description : str
    how_to_handle: Optional[str]
    expected_downtime_minutes: Optional[int] = None

class BreakDownCodeUpdate(BaseModel):
    description: Optional[str] = None
    how_to_handle: Optional[str] = None
    expected_downtime_minutes: Optional[int] = None

class BreakDownOut(BaseModel):
    breakdown_code : int
    description : str
    how_to_handle: Optional[str]
    expected_downtime_minutes: Optional[int] = None
    class Config:
        from_attributes = True
