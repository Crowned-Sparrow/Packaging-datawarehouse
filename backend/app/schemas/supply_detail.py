from pydantic import BaseModel
from datetime import date

class SupplyDetailCreate(BaseModel):
    supplier_id: int
    material_id:int
    quantity: int
    unit_price: float
    request_date:date
    receive_date:date

class SupplyDetailUpdate(BaseModel):
    receive_date: date

class SupplyDetailOut(BaseModel):
    supply_detail_id: int
    supplier_id: int
    material_id:int
    quantity: int
    unit_price: float
    request_date:date
    receive_date:date

    class Config:
        from_attributes = True
