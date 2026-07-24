from __future__ import annotations

from pathlib import Path
from typing import Any


class ParquetWriter:
    def __init__(self, output_dir: str | Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write(self, dataset_name: str, rows: list[dict[str, Any]]) -> Path:
        if not rows:
            raise ValueError("rows cannot be empty when writing parquet")

        try:
            import polars as pl
        except ImportError as exc:
            raise ImportError(
                "Parquet export requires polars. Install it before running this load step."
            ) from exc

        target_path = self.output_dir / f"{dataset_name}.parquet"
        frame = pl.from_dicts(rows)
        frame.write_parquet(target_path)
        return target_path
