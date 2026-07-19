from pydantic import BaseModel, EmailStr

class SupplierCreate(BaseModel):
    supplier_name: str
    contact_phone : str
    contact_email : EmailStr

class SupplierOut(BaseModel):
    supplier_id :int
    supplier_name: str
    contact_phone : str
    contact_email : EmailStr

    class Config:
        from_attributes = True 