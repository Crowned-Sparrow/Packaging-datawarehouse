#backend/app/security
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

import os
from pathlib import Path
from dotenv import load_dotenv
import os
from pathlib import Path

# Lấy đường dẫn tới thư mục hiện tại của file security.py
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_path = BASE_DIR / "backend" / "app" / "core" / "login.env"

load_dotenv(dotenv_path=env_path)
SECRET_KEY = os.environ.get("SECRET_KEY","")
ALGORITHM = os.environ.get("ALGORITHM","")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY chưa được cấu hình trong biến môi trường")

# bcrypt tự sinh salt ngẫu nhiên cho mỗi mật khẩu và tự nhúng vào chuỗi hash,
# nên không cần cột "salt" riêng trong database.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Dùng khi TẠO tài khoản nhân viên mới, trước khi lưu vào hash_password."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """So khớp mật khẩu người dùng nhập với hash lưu trong DB (constant-time)."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
    
