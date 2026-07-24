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
class PostgresWriteConfig:
    user: str
    password: str
    host: str
    port: int | str
    database: str

    @classmethod
    def from_env(cls) -> "PostgresWriteConfig":
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


class PostgresWriter:
    def __init__(self, engine: Engine):
        self.engine = engine

    @classmethod
    def from_env(cls) -> "PostgresWriter":
        config = PostgresWriteConfig.from_env()
        engine = create_engine(config.to_url(), pool_pre_ping=True)
        return cls(engine=engine)

    def write_rows(
        self,
        schema: str,
        table: str,
        rows: list[dict[str, Any]],
        mode: str = "append",
    ) -> int:
        if not rows:
            return 0

        safe_schema = _validate_identifier(schema)
        safe_table = _validate_identifier(table)

        columns = list(rows[0].keys())
        if not columns:
            raise ValueError("rows must contain at least one column")

        for column in columns:
            _validate_identifier(column)

        quoted_columns = ", ".join(f'"{column}"' for column in columns)
        bind_columns = ", ".join(f":{column}" for column in columns)
        insert_sql = (
            f'INSERT INTO "{safe_schema}"."{safe_table}" ({quoted_columns}) '
            f"VALUES ({bind_columns})"
        )

        with self.engine.begin() as connection:
            if mode == "replace":
                connection.execute(text(f'TRUNCATE TABLE "{safe_schema}"."{safe_table}"'))
            elif mode != "append":
                raise ValueError("mode must be either 'append' or 'replace'")

            connection.execute(text(insert_sql), rows)

        return len(rows)

    def close(self) -> None:
        self.engine.dispose()
