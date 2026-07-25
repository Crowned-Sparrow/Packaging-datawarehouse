from pydantic import BaseModel

class ProductCreate(BaseModel):
    pds: str

class ProductOut(BaseModel):
    product_id: int
    pds: str
    class Config:
        from_attributes = True

class CorrugatingProductCreate(ProductCreate):
    length: float
    width: float
    unit: float

class CorrugatingProductOut(ProductOut):
    length: float
    width: float
    unit: float
