from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.material import Material
from app.models.employee import Employee
from app.schemas.material import MaterialCreate, MaterialOut, MaterialUpdate
from app.dependencies import get_current_employee

router = APIRouter(prefix="/api/materials", tags=["materials"])

@router.post("/add", response_model=MaterialOut)
def add_material(
    payload: MaterialCreate,
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee),
):
    try:
        material = Material(
            material_code=payload.material_code,
            material_name=payload.material_name,
            material_type=payload.material_type,
            unit=payload.unit,
        )
        db.add(material)
        db.commit()
        db.refresh(material)
        return material
    except Exception as e:
        print(f"Error adding material: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error adding material: {str(e)}",
        )

@router.get("/list", response_model=List[MaterialOut])
def list_materials(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    material_code: Optional[str] = None,
    material_name: Optional[str] = None,
    material_type: Optional[str] = None,
    current_employee: Employee = Depends(get_current_employee),
):
    query = db.query(Material)
    if material_code:
        query = query.filter(Material.material_code.ilike(f"%{material_code}%"))
    if material_name:
        query = query.filter(Material.material_name.ilike(f"%{material_name}%"))
    if material_type:
        query = query.filter(Material.material_type == material_type)
    return query.offset(skip).limit(limit).all()

@router.get("/find/{material_id}", response_model=MaterialOut)
def find_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee),
):
    material = db.query(Material).filter(Material.material_id == material_id).first()
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Material with id {material_id} not found",
        )
    return material

@router.patch("/update/{material_id}", response_model=MaterialOut)
def update_material(
    material_id: int,
    payload: MaterialUpdate,
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee),
):
    material = db.query(Material).filter(Material.material_id == material_id).first()
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Material with id {material_id} not found",
        )

    if payload.material_code is not None:
        material.material_code = payload.material_code
    if payload.material_name is not None:
        material.material_name = payload.material_name
    if payload.material_type is not None:
        material.material_type = payload.material_type
    if payload.unit is not None:
        material.unit = payload.unit

    try:
        db.commit()
        db.refresh(material)
        return material
    except Exception as e:
        print(f"Error updating material: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating material: {str(e)}",
        )
