from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from app.core.database import get_db

from app.models.supplier import Supplier
from app.models.supply_detail import SupplyDetail
from app.models.employee import Employee

from app.schemas.supplier import SupplierCreate, SupplierOut
from app.schemas.supply_detail import SupplyDetailCreate, SupplyDetailOut, SupplyDetailUpdate
from app.dependencies import get_current_employee

router = APIRouter(prefix="/api/supplies", tags=["supplies"])
@router.post("/add/suppliers", response_model=SupplierOut)
def add_supplier(
    payload: SupplierCreate,
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee)
):
    try:
        supplier = Supplier(
            supplier_name = payload.supplier_name,
            contact_email = payload.contact_email,
            contact_phone = payload.contact_phone
        )
        db.add(supplier)
        db.commit()
        db.refresh(supplier)
        return supplier
    except Exception as e:
        print(f"Error adding supplier: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error adding supplier: {str(e)}"
        )

@router.get("/list/suppliers", response_model=List[SupplierOut])
def list_supplier(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    name: str | None = None,
    title: str | None = None,
    current_employee: Employee = Depends(get_current_employee),
):
    query = db.query(Supplier)
    if name:
        query = query.filter(Supplier.supplier_name.ilike(f"%{name}%"))
    return query.offset(skip).limit(limit).all()


@router.get("/find/suppliers/{supplier_id}", response_model=SupplierOut)
def find_supplier(supplier_id: int, db: Session = Depends(get_db),
                  current_employee: Employee = Depends(get_current_employee)):
    supplier = db.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Supplier with id {supplier_id} not found")
    return supplier

@router.post("/add/supply_details", response_model=SupplyDetailOut)
def add_supply_detail(
    payload: SupplyDetailCreate,
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee)
):
    try:
        supply_detail = SupplyDetail(
            supplier_id=payload.supplier_id,
            material_id=payload.material_id,
            quantity = payload.quantity,
            request_date=payload.request_date,
            receive_date = payload.receive_date
        )
        db.add(supply_detail)
        db.commit()
        db.refresh(supply_detail)
        return supply_detail
    except Exception as e:
        print(f"Error adding supply_detail: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error adding supply_detail: {str(e)}"
        )
    
@router.get("/list/supply_details", response_model=List[SupplyDetailOut])
def list_supply_detail(
    receive_date: date,
    request_date: date,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_employee: Employee = Depends(get_current_employee),
):
    query = db.query(SupplyDetail)
    if status:
        query = query.filter(SupplyDetail.order_status == status)
    return query.offset(skip).limit(limit).all()

@router.get("/find/supply_details/{supply_detail_id}", response_model=SupplyDetailOut)
def find_supply_detail(
    supply_detail_id: int,
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee),
):
    supply_detail = db.query(SupplyDetail).filter(SupplyDetail.supply_detail_id == supply_detail_id).first()
    if not supply_detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {supply_detail_id} not found",
        )
    return supply_detail

@router.get("/update/supply_details/{supply_detail_id}",response_model= SupplyDetailOut)
def update_detail(
        supply_detail_id: int,
        receive_date: date,
        db: Session = Depends(get_db),
        current_employee: Employee = Depends(get_current_employee)
):
    supply_detail = db.query(SupplyDetail).filter(SupplyDetail.supply_detail_id == supply_detail_id).first()
    if not supply_detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supply detail with id {supply_detail_id} not found",
        )

    if supply_detail.receive_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Supply detail already has receive date: {supply_detail.receive_date}",
        )
    supply_detail.receive_date = receive_date
    db.commit()
    db.refresh(supply_detail)
    return supply_detail