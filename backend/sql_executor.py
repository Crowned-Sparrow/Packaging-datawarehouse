import os
import logging
from pathlib import Path
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, Connection, URL

logger = logging.getLogger(__name__)

# ── Engine ─────────────────────────────────────────────────────────────────────
# Trong SQLAlchemy, ta tạo 1 Engine dùng chung cho cả app (connection pool),
# thay vì mở 1 connection riêng lẻ như psycopg2.connect().

def get_engine() -> Engine:
    user     = os.environ.get("PG_USER", "")
    password = os.environ.get("PG_PASSWORD", "")   # không nên để default password thật trong code
    host     = os.environ.get("PG_HOST", "")
    port     = os.environ.get("PG_PORT", )
    db       = os.environ.get("PG_DB", "")

    url = URL.create(
    drivername="postgresql+psycopg2",
    username=user,
    password=password,  # để nguyên password gốc có @, không cần tự encode
    host=host,
    port=port,
    database=db,
    )
    # pool_pre_ping: tự kiểm tra & tái tạo connection chết trước khi dùng
    # print('Get engine')
    return create_engine(url, pool_pre_ping=True)


# ── Types ──────────────────────────────────────────────────────────────────────

Params      = dict
ParamsList  = list[dict]
ParamsInput = Params | ParamsList


# ── SQLExecutor ────────────────────────────────────────────────────────────────

class SQLExecutor:
    def __init__(self, engine: Engine, logger= None):
        self.engine = engine
        self.logger = logger or logging.getLogger(__name__)

    def run_path(self, conn, path: Path):
        """Chạy 1 file, hoặc toàn bộ file .sql trong 1 folder (theo thứ tự tên)."""
        if path.is_dir():
            files = sorted(path.glob("*.sql"))
            if not files:
                raise FileNotFoundError(f"[SQL EX]: Không có file .sql nào trong {path}")
            for f in files:
                self.run_path(conn, f)
        elif path.exists():
            self.logger.info(f"[SQL EX]: execute {path}")
            conn.execute(text(path.read_text(encoding="utf-8")))
        else:
            raise FileNotFoundError(f"[SQL EX]: không tìm thấy {path}")

    def init_schema(
        self,
        conn,
        mother_path: str | Path = "SQL/Public",
        schema: str | None = None,
        ordered_list=("tables", "constraints.sql", "functions", "triggers"),
    ):
        """Khởi tạo 1 schema theo thứ tự file/folder đã cho."""
        mother_path = Path(mother_path)
        if schema:
            conn.execute(text(f'SET search_path TO "{schema}", public'))
        self.logger.info(f"[SQL EX]: Init schema '{schema or 'public'}' từ {mother_path}")
        for item in ordered_list:
            self.run_path(conn, mother_path / item)

    def init_database(
        self,
        mother_path: str | Path = "SQL",
        schema_folder_map: dict[str, str | None] = None,
    ):
        """
        Khởi tạo toàn bộ database. schema_folder_map: {tên_folder: tên_schema}.
        schema=None nghĩa là dùng search_path mặc định (public).
        Toàn bộ chạy trong 1 transaction duy nhất — lỗi bất kỳ đâu sẽ rollback hết.
        """
        if schema_folder_map is None:
            schema_folder_map = {"public": None, "corrugating": "corrugating"}
        mother_path = Path(mother_path)
        with self.engine.begin() as conn:   # mở transaction 1 LẦN duy nhất, không lồng
            self.logger.info(f"[SQL EX]: Init database từ {mother_path}")
            for folder, schema in schema_folder_map.items():
                self.init_schema(conn, mother_path / folder, schema=schema)
            self.logger.info("[SQL EX]: Init database COMPLETED")
