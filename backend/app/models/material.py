from sqlalchemy import Column, Integer, String, CheckConstraint
from app.core.database import Base

class Material(Base):
    __tablename__ = "dim_materials"

    material_id = Column(Integer, primary_key=True, autoincrement=True)
    material_code = Column(String(50), nullable=False, unique=True)
    material_name = Column(String(100), nullable=False) 
    material_type = Column(String(50), nullable=False)
    unit = Column(String(20), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "material_type IN ('paper', 'ink', 'glue', 'other')", 
            name="check_material_type"
        ),
        CheckConstraint(
            "unit IN ('kg', 'liter', 'sheet', 'roll', 'other')", 
            name="check_unit"
        ),
    )

    def __repr__(self):
        return f"<Material id={self.material_id} code={self.material_code!r} name={self.material_name!r}>"
