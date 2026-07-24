from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, URL

IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _validate_identifier(name: str) -> str:
    if not IDENTIFIER_PATTERN.match(name):
        raise ValueError(f"Invalid SQL identifier: {name}")
    return name


@dataclass(frozen=True)
class PostgresConfig:
    user: str
    password: str
    host: str
    port: int | str
    database: str

    @classmethod
    def from_env(cls) -> "PostgresConfig":
        return cls(
            user=os.environ.get("PG_USER", ""),
            password=os.environ.get("PG_PASSWORD", ""),
            host=os.environ.get("PG_HOST", ""),
            port=os.environ.get("PG_PORT", "5432"),
            database=os.environ.get("PG_DB", ""),
        )

    def to_url(self) -> URL:
        return URL.create(
            drivername="postgresql+psycopg2",
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database,
        )


class PostgresReader:
    """Extractor cho PostgreSQL, trả dữ liệu dạng list[dict]."""

    def __init__(self, engine: Engine):
        self.engine = engine

    @classmethod
    def from_env(cls) -> "PostgresReader":
        config = PostgresConfig.from_env()
        engine = create_engine(config.to_url(), pool_pre_ping=True)
        return cls(engine=engine)

    def fetch_all(
        self,
        sql: str,
        params: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        with self.engine.connect() as conn:
            result = conn.execute(text(sql), params or {})
            return [dict(row._mapping) for row in result]

    def extract_table(
        self,
        schema: str,
        table: str,
        columns: list[str] | None = None,
        where_clause: str | None = None,
        params: dict[str, Any] | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        safe_schema = _validate_identifier(schema)
        safe_table = _validate_identifier(table)

        if columns:
            safe_columns = ", ".join(_validate_identifier(col) for col in columns)
        else:
            safe_columns = "*"

        sql = f'SELECT {safe_columns} FROM "{safe_schema}"."{safe_table}"'

        if where_clause:
            sql += f" WHERE {where_clause}"
        if limit is not None:
            sql += " LIMIT :limit"
            params = {**(params or {}), "limit": limit}

        return self.fetch_all(sql=sql, params=params)

    def extract_incremental(
        self,
        schema: str,
        table: str,
        cursor_column: str,
        last_cursor_value: Any,
        columns: list[str] | None = None,
        batch_size: int = 1000,
    ) -> list[dict[str, Any]]:
        safe_cursor = _validate_identifier(cursor_column)
        where_clause = f"{safe_cursor} > :last_cursor_value ORDER BY {safe_cursor}"
        params = {"last_cursor_value": last_cursor_value}
        return self.extract_table(
            schema=schema,
            table=table,
            columns=columns,
            where_clause=where_clause,
            params=params,
            limit=batch_size,
        )

    def close(self) -> None:
        self.engine.dispose()