from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeOut
from app.security import hash_password  # hàm hash có sẵn, dùng chung với auth.py
from app.dependencies import get_current_employee

router = APIRouter(prefix="/api/employees", tags=["employees"])

@router.post("/add", response_model=EmployeeOut)
def add_employee(payload: EmployeeCreate, db: Session = Depends(get_db)
                 ,current_employee: Employee = Depends(get_current_employee)):
    employee = Employee(
        employee_name=payload.employee_name,
        title=payload.title,
        contact_email=payload.contact_email,
        contact_phone=payload.contact_phone,
        hash_password=hash_password(payload.password),
    )
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee

@router.get("/list", response_model=List[EmployeeOut])
def list_employee(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    name: str | None = None,
    title: str | None = None,
    current_employee: Employee = Depends(get_current_employee),
):
    query = db.query(Employee)
    if name:
        query = query.filter(Employee.employee_name.ilike(f"%{name}%"))
    if title:
        query = query.filter(Employee.title.ilike(f"%{title}%"))
    return query.offset(skip).limit(limit).all()


@router.get("/find/{employee_id}", response_model=EmployeeOut)
def find_employee(employee_id: int, db: Session = Depends(get_db),
                  current_employee: Employee = Depends(get_current_employee)):
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Employee with id {employee_id} not found")
    return employee

@router.get("/me", response_model=EmployeeOut)
def get_my_profile(current_employee: Employee = Depends(get_current_employee)):
    return current_employee