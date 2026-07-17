from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerOut
from app.models.employee import Employee
from app.security import hash_password  # hàm hash có sẵn, dùng chung với auth.py
from app.dependencies import get_current_employee

router = APIRouter(prefix="/api/customers", tags=["customers"])
@router.post("/add",response_model=CustomerOut)
def add_customer(payload: CustomerCreate, db: Session = Depends(get_db)
                 ,current_employee: Employee = Depends(get_current_employee)):
    customer = Customer(
        customer_name = payload.customer_name,
        contact_email = payload.contact_email,
        contact_phone = payload.contact_phone
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer

@router.get("/list", response_model=List[CustomerOut])
def list_customer(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    name: str | None = None,
    title: str | None = None,
    current_employee: Employee = Depends(get_current_employee),
):
    query = db.query(Customer)
    if name:
        query = query.filter(Customer.customer_name.ilike(f"%{name}%"))
    return query.offset(skip).limit(limit).all()


@router.get("/find/{customer_id}", response_model=CustomerOut)
def find_customer(customer_id: int, db: Session = Depends(get_db),
                  current_employee: Employee = Depends(get_current_employee)):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Customer with id {customer_id} not found")
    return customer


