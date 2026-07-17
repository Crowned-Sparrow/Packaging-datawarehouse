from pydantic import BaseModel, EmailStr

class CustomerCreate(BaseModel):
    customer_name: str
    contact_email : EmailStr
    contact_phone : str

class CustomerOut(BaseModel):
    customer_id: int
    customer_name: str
    contact_email : EmailStr
    contact_phone : str

    class Config:
        from_attributes = True
