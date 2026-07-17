from pydantic import BaseModel, EmailStr

class EmployeeCreate(BaseModel):
    employee_name: str
    title: str
    contact_email : EmailStr
    contact_phone : str
    password: str ## chưa hash

class EmployeeOut(BaseModel):
    employee_name: str
    title: str
    contact_email : EmailStr
    contact_phone : str

    class Config:
        from_attributes = True