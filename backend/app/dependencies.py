# app/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.employee import Employee
from app.security import decode_access_token

# tokenUrl chỉ để Swagger UI biết gọi đâu để lấy token, không ảnh hưởng logic
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_employee(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Employee:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không thể xác thực, vui lòng đăng nhập lại",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    employee_id = payload.get("sub")
    if employee_id is None:
        raise credentials_exception

    employee = db.query(Employee).filter(Employee.employee_id == int(employee_id)).first()
    if employee is None:
        raise credentials_exception

    return employee