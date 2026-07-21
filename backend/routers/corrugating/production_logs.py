from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.core.database import get_db
from app.models.production_log import CorrugatingProductionLog
from app.models.employee import Employee
from app.schemas.production_log import CorrugatingProductionLogCreate, CorrugatingProductionLogOut, CorrugatingUpdateProductionLog
from app.dependencies import get_current_employee
from .router import router
from typing import Optional

@router.post("/add", response_model= CorrugatingProductionLogOut)
def add_machine(payload: CorrugatingProductionLogCreate, db: Session = Depends(get_db)
                ,current_employee: Employee = Depends(get_current_employee)):
    try:
        log = CorrugatingProductionLog(
            pds = payload.pds,
            leader_id = payload.leader_id,
            operator_id = payload.operator_id,
            manager_id = payload.manager_id,
            supervisor_id = payload.supervisor_id,
            start_time = payload.start_time,
            log_note = payload.log_note,
            machine_id = payload.machine_id,
            product_id = payload.product_id,
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
    except Exception as e:
        print(f"Error adding production log: {e}")##
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error adding production log: {str(e)}"##
        )

@router.get("/list", response_model= List[CorrugatingProductionLogOut])
def list_machine(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    pds: Optional[str] = None,
    machine_id: Optional[int] = None,
    current_employee: Employee = Depends(get_current_employee),
):
    query = db.query(CorrugatingProductionLog)##
    if start_time:
        query = query.filter(CorrugatingProductionLog.start_time > start_time)##
    if end_time:
        query = query.filter(CorrugatingProductionLog.end_time < end_time)
    if machine_id:
        query = query.filter(CorrugatingProductionLog.machine_id == machine_id)
    if pds:
        query = query.filter(CorrugatingProductionLog.pds == pds)
    return query.offset(skip).limit(limit).all()


@router.get("/find/{production_log_id}", response_model=CorrugatingProductionLogOut)
def find_order(
    production_log_id: int,
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee),
):
    log = db.query(CorrugatingProductionLog).filter(CorrugatingProductionLog.production_log_id == production_log_id).first()##
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine with id {production_log_id} not found",
        )
    return log

@router.patch("/update/{production_log_id}", response_model=CorrugatingProductionLogOut)
def update_production_log(
    production_log_id: int,
    payload: CorrugatingUpdateProductionLog,
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee),
):
    log = (
        db.query(CorrugatingProductionLog)
        .filter(CorrugatingProductionLog.production_log_id == production_log_id)
        .first()
    )
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Production log with id {production_log_id} not found",
        )

    # Không cho cập nhật lại 1 log đã kết thúc (tránh ghi đè số liệu đã chốt)
    if log.end_time is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Production log {production_log_id} already ended at {log.end_time}",
        )

    # Kiểm tra end_time hợp lệ trước khi đụng DB, để trả lỗi rõ ràng
    # thay vì để CHECK constraint CK_time raise IntegrityError khó đọc
    if payload.end_time < log.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="end_time before start_time",
        )

    log.end_time = payload.end_time
    log.product_weight = payload.product_weight
    log.material_weight = payload.material_weight
    log.cut_pallet_count = payload.cut_pallet_count
    log.waste_endroll_weight = payload.waste_endroll_weight
    log.waste_trim_weight = payload.waste_trim_weight
    log.waste_production_weight = payload.waste_production_weight
    log.waste_core_weight = payload.waste_core_weight

    try:
        db.commit()
        db.refresh(log)
        return log
    except Exception as e:
        print(f"Error updating production log: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating production log: {str(e)}",
        )