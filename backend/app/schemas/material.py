from typing import Optional
from pydantic import BaseModel

class MaterialCreate(BaseModel):
    material_code: str
    material_name : str
    material_type : str
    unit : str

class MaterialUpdate(BaseModel):
    material_code: Optional[str] = None
    material_name: Optional[str] = None
    material_type: Optional[str] = None
    unit: Optional[str] = None

class MaterialOut(BaseModel):
    material_id :int
    material_code: str
    material_name : str
    material_type : str
    unit : str

    class Config:
        from_attributes = True
