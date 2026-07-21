from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ProductionLogCreate(BaseModel):
    leader_id: int
    manager_id: int
    operator_id: int
    supervisor_id: int
    start_time: datetime
    pds: str
    log_note: Optional[str] = None


class UpdateProductionLog(BaseModel):
    end_time: datetime
    product_weight: float
    material_weight: float


class ProductionLogOut(BaseModel):
    #model_config = ConfigDict(from_attributes=True)

    production_log_id: int
    pds: str
    start_time: datetime
    end_time: Optional[datetime] = None
    product_weight: Optional[float] = None
    material_weight: Optional[float] = None

    class Config:
        from_attributes = True

class CorrugatingProductionLogCreate(ProductionLogCreate):
    machine_id: int
    product_id: int


class CorrugatingUpdateProductionLog(UpdateProductionLog):
    cut_pallet_count: int
    waste_endroll_weight: float
    waste_trim_weight: float
    waste_production_weight: float
    waste_core_weight: float


class CorrugatingProductionLogOut(ProductionLogOut):
    cut_pallet_count: Optional[int] = None
    waste_endroll_weight: Optional[float] = None
    waste_trim_weight: Optional[float] = None
    waste_production_weight: Optional[float] = None
    waste_core_weight: Optional[float] = None