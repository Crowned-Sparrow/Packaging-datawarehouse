from sqlalchemy.engine import Engine, URL
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os

def get_url()-> URL:
    user     = os.environ.get("PG_USER", "")
    password = os.environ.get("PG_PASSWORD", "")
    host     = os.environ.get("PG_HOST", "")
    port     = os.environ.get("PG_PORT", )
    db       = os.environ.get("PG_DB", "")
    
    url = URL.create(
        drivername="postgresql+psycopg2",
        username= user,
        password= password,
        host= host,
        port= port,
        database= db
    )
    return 

def get_engine() -> Engine:
    url = get_url()
    # pool_pre_ping: tự kiểm tra & tái tạo connection chết trước khi dùng
    # print('Get engine')
    return create_engine(url, pool_pre_ping=True)

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
 
def get_db():
    """Dependency FastAPI: mở session DB cho mỗi request, tự đóng khi xong."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()