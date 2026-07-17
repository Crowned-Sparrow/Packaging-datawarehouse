from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.core.database import get_db
from app.models.order import Order
from app.models.employee import Employee
from app.schemas.order import OrderCreate, OrderOut, OrderAssignPDS
from app.dependencies import get_current_employee

router = APIRouter(prefix="/api/orders", tags=["orders"])

def generate_pds(order_id: int, order_date: datetime.date) -> str:
    """
    Generate PDS code: ddmmyys
    dd: day, mm: month, yy: year (2 digits), s: order_id
    Example: 16071625 for 16 July 2026, order_id=5
    """
    day = str(order_date.day).zfill(2)
    month = str(order_date.month).zfill(2)
    year = str(order_date.year)[-2:]  # Last 2 digits of year
    order_id_str = str(order_id)
    return f"{day}{month}{year}{order_id_str}"

@router.post("/add", response_model=OrderOut)
def add_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee),
):
    try:
        order = Order(
            customer_id=payload.customer_id,
            order_date=payload.order_date,
            delivery_date=payload.delivery_date,
            quantity=payload.quantity,
            order_note=payload.order_note,
            order_status="pending",
        )
        db.add(order)
        db.commit()
        db.refresh(order)
        return order
    except Exception as e:
        print(f"Error adding order: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error adding order: {str(e)}"
        )

@router.get("/list", response_model=List[OrderOut])
def list_orders(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: str | None = None,
    current_employee: Employee = Depends(get_current_employee),
):
    query = db.query(Order)
    if status:
        query = query.filter(Order.order_status == status)
    return query.offset(skip).limit(limit).all()

@router.get("/find/{order_id}", response_model=OrderOut)
def find_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee),
):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {order_id} not found",
        )
    return order

@router.post("/assign-pds/{order_id}", response_model=OrderOut)
def assign_pds(
    order_id: int,
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee),
):
    """
    Assign PDS to an order when deciding to produce.
    PDS format: ddmmyys (day, month, year, order_id)
    """
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {order_id} not found",
        )

    if order.pds:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order already has PDS: {order.pds}",
        )

    # Generate PDS
    pds = generate_pds(order_id, order.order_date)
    order.pds = pds
    order.order_status = "in_progress"

    db.commit()
    db.refresh(order)
    return order
