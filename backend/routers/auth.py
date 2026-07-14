from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import Employee
from schemas import LoginRequest, TokenResponse
from security import create_access_token, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.contact_email == payload.email).first()

    # Cố ý trả cùng 1 thông báo dù email không tồn tại hay sai mật khẩu,
    # để không lộ email nào đang tồn tại trong hệ thống.
    if not employee or not verify_password(payload.password, employee.hash_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không đúng",
        )

    access_token = create_access_token(
        data={"sub": str(employee.employee_id), "email": employee.contact_email}
    )

    return TokenResponse(
        access_token=access_token,
        employee_name=employee.employee_name,
        title=employee.title,
    )