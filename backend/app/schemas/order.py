from pydantic import BaseModel
from datetime import date

class OrderCreate(BaseModel):
    customer_id: int
    order_date: date
    delivery_date: date | None = None
    quantity: int
    order_note: str | None = None

class OrderUpdate(BaseModel):
    order_status: str | None = None

class OrderAssignPDS(BaseModel):
    pds: str

class OrderOut(BaseModel):
    order_id: int
    pds: str | None
    customer_id: int
    order_date: date
    delivery_date: date | None
    quantity: int
    order_note: str | None
    order_status: str

    class Config:
        from_attributes = True
