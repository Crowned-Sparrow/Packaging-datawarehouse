from pydantic import BaseModel

class MaterialCreate(BaseModel):
    material_code: str
    material_name : str
    material_type : str
    unit : str

class MaterialOut(BaseModel):
    material_id :int
    material_code: str
    material_name : str
    material_type : str
    unit : str

    class Config:
        from_attributes = True
