from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.machine import CorrugatingMachine
from app.models.employee import Employee
from app.schemas.machine import CorrugatingMachineCreate, CorrugatingMachineOut, MachineUpdateStatus
from app.dependencies import get_current_employee
from .router import router
router = APIRouter(prefix="/machines", tags=["machines"])

@router.post("/add", response_model= CorrugatingMachineOut)
def add_machine(payload: CorrugatingMachineCreate, db: Session = Depends(get_db)
                ,current_employee: Employee = Depends(get_current_employee)):
    try:
        machine = CorrugatingMachine(
            machine_name = payload.machine_name,
            lead_operator_id = payload.lead_operator_id,
        )
        db.add(machine)
        db.commit()
        db.refresh(machine)
        return machine
    except Exception as e:
        print(f"Error adding machine: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error adding machine: {str(e)}"
        )

@router.get("/list", response_model= List[CorrugatingMachineOut])
def list_machine(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: str | None = None,
    current_employee: Employee = Depends(get_current_employee),
):
    query = db.query(CorrugatingMachine)
    if status:
        query = query.filter(CorrugatingMachine.machine_status == status)
    return query.offset(skip).limit(limit).all()

@router.get("/find/{machine_id}", response_model=CorrugatingMachineOut)
def find_order(
    machine_id: int,
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee),
):
    order = db.query(CorrugatingMachine).filter(CorrugatingMachine.machine_id == machine_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine with id {machine_id} not found",
        )
    return order