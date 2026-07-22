from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.breakdown_code import BreakDownCode
from app.models.breakdown_log import MachineBreakDownLog
from app.models.employee import Employee
from app.schemas.breakdown_code import (
    BreakDownCodeCreate,
    BreakDownCodeUpdate,
    BreakDownOut,
)
from app.schemas.breakdown_log import (
    MachineBreakdownLogCreate,
    MachineBreakDownLogOut,
    UpdateMachineBreakDownLog,
)
from app.dependencies import get_current_employee
from .router import router

@router.post("/breakdown-codes/add", response_model=BreakDownOut)
def add_breakdown_code(
    payload: BreakDownCodeCreate,
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee),
):
    try:
        breakdown_code = BreakDownCode(
            description=payload.description,
            how_to_handle=payload.how_to_handle,
            expected_downtime_minutes=payload.expected_downtime_minutes,
        )
        db.add(breakdown_code)
        db.commit()
        db.refresh(breakdown_code)
        return breakdown_code
    except Exception as e:
        print(f"Error adding breakdown code: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error adding breakdown code: {str(e)}",
        )

@router.get("/breakdown-codes/list", response_model=List[BreakDownOut])
def list_breakdown_codes(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    description: Optional[str] = None,
    current_employee: Employee = Depends(get_current_employee),
):
    query = db.query(BreakDownCode)
    if description:
        query = query.filter(BreakDownCode.description.ilike(f"%{description}%"))
    return query.offset(skip).limit(limit).all()

@router.get("/breakdown-codes/find/{breakdown_code}", response_model=BreakDownOut)
def find_breakdown_code(
    breakdown_code: int,
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee),
):
    code = db.query(BreakDownCode).filter(BreakDownCode.breakdown_code == breakdown_code).first()
    if not code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Breakdown code {breakdown_code} not found",
        )
    return code

@router.patch("/breakdown-codes/update/{breakdown_code}", response_model=BreakDownOut)
def update_breakdown_code(
    breakdown_code: int,
    payload: BreakDownCodeUpdate,
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee),
):
    code = db.query(BreakDownCode).filter(BreakDownCode.breakdown_code == breakdown_code).first()
    if not code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Breakdown code {breakdown_code} not found",
        )
    if payload.description is not None:
        code.description = payload.description
    if payload.how_to_handle is not None:
        code.how_to_handle = payload.how_to_handle
    if payload.expected_downtime_minutes is not None:
        code.expected_downtime_minutes = payload.expected_downtime_minutes

    try:
        db.commit()
        db.refresh(code)
        return code
    except Exception as e:
        print(f"Error updating breakdown code: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating breakdown code: {str(e)}",
        )

@router.post("/breakdown-logs/add", response_model=MachineBreakDownLogOut)
def add_breakdown_log(
    payload: MachineBreakdownLogCreate,
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee),
):
    try:
        breakdown_log = MachineBreakDownLog(
            machine_id=payload.machine_id,
            supervisor_id=payload.supervisor_id,
            breakdown_code=payload.breakdown_code,
            pds=payload.pds,
            breakdown_time=payload.breakdown_time,
            breakdown_note=payload.breakdown_note,
        )
        db.add(breakdown_log)
        db.commit()
        db.refresh(breakdown_log)
        return breakdown_log
    except Exception as e:
        print(f"Error adding breakdown log: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error adding breakdown log: {str(e)}",
        )

@router.get("/breakdown-logs/list", response_model=List[MachineBreakDownLogOut])
def list_breakdown_logs(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    machine_id: Optional[int] = None,
    supervisor_id: Optional[int] = None,
    breakdown_code: Optional[int] = None,
    pds: Optional[str] = None,
    current_employee: Employee = Depends(get_current_employee),
):
    query = db.query(MachineBreakDownLog)
    if start_time:
        query = query.filter(MachineBreakDownLog.breakdown_time >= start_time)
    if end_time:
        query = query.filter(MachineBreakDownLog.breakdown_time <= end_time)
    if machine_id:
        query = query.filter(MachineBreakDownLog.machine_id == machine_id)
    if supervisor_id:
        query = query.filter(MachineBreakDownLog.supervisor_id == supervisor_id)
    if breakdown_code:
        query = query.filter(MachineBreakDownLog.breakdown_code == breakdown_code)
    if pds:
        query = query.filter(MachineBreakDownLog.pds.ilike(f"%{pds}%"))
    return query.offset(skip).limit(limit).all()

@router.get("/breakdown-logs/find/{breakdown_log_id}", response_model=MachineBreakDownLogOut)
def find_breakdown_log(
    breakdown_log_id: int,
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee),
):
    log = db.query(MachineBreakDownLog).filter(MachineBreakDownLog.breakdown_log_id == breakdown_log_id).first()
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Breakdown log {breakdown_log_id} not found",
        )
    return log

@router.patch("/breakdown-logs/update/{breakdown_log_id}", response_model=MachineBreakDownLogOut)
def update_breakdown_log(
    breakdown_log_id: int,
    payload: UpdateMachineBreakDownLog,
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee),
):
    log = db.query(MachineBreakDownLog).filter(MachineBreakDownLog.breakdown_log_id == breakdown_log_id).first()
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Breakdown log {breakdown_log_id} not found",
        )
    if payload.recovery_time < log.breakdown_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recovery time cannot be earlier than breakdown time",
        )

    log.recovery_time = payload.recovery_time
    if payload.breakdown_note is not None:
        log.breakdown_note = payload.breakdown_note

    try:
        db.commit()
        db.refresh(log)
        return log
    except Exception as e:
        print(f"Error updating breakdown log: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating breakdown log: {str(e)}",
        )
