from typing import Any

from pydantic import BaseModel, Field


class AskSQLRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000)


class AskSQLResponse(BaseModel):
    sql: str
    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int
    truncated: bool


class ExplainRiskRequest(BaseModel):
    machine_name: str = Field(..., min_length=1, max_length=100)
    median_days_to_breakdown: float | None = None
    relative_risk_score: float


class ExplainRiskResponse(BaseModel):
    explanation: str
