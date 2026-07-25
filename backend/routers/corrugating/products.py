from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db

from app.models.product import CorrugatingProduct
from app.models.employee import Employee
from app.schemas.product import CorrugatingProductCreate, CorrugatingProductOut
from app.dependencies import get_current_employee
from typing import Optional

@router.post("/add", response_model= CorrugatingProductOut)
def add_product(payload: CorrugatingProductCreate, db: Session = Depends(get_db)
                ,current_employee: Employee = Depends(get_current_employee)):
    try:
        product = CorrugatingProduct(
            pds = payload.pds,
            unit = payload.unit,
            length = payload.length,
            width = payload.width
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        return product
    except Exception as e:
        print(f"Error adding product: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error adding product: {str(e)}"
        )

@router.get("/list", response_model= List[CorrugatingProductOut])
def list_machine(
    pds:Optional[str],
    max_length: Optional[float],
    min_length:Optional[float],
    max_width:Optional[float],
    min_width:Optional[float],
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_employee: Employee = Depends(get_current_employee),
):
    query = db.query(CorrugatingProduct)
    if pds:
        query = query.filter(CorrugatingProduct.pds == pds)
    if max_length:
        query = query.filter(CorrugatingProduct.length <= max_length)
    if min_length:
        query = query.filter(CorrugatingProduct.length >= min_length)
    if max_width:
        query = query.filter(CorrugatingProduct.width <= max_width)
    if min_width:
        query = query.filter(CorrugatingProduct.width >= min_width)
    return query.offset(skip).limit(limit).all()

@router.get("/find/{product_id}", response_model=CorrugatingProductOut)
def find_order(
    product_id: int,
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee),
):
    product = db.query(CorrugatingProduct).filter(CorrugatingProduct.product_id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found",
        )
    return product