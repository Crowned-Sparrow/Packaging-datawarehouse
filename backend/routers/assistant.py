import re

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_employee
from app.schemas.assistant import (
    AskSQLRequest,
    AskSQLResponse,
    ExplainRiskRequest,
    ExplainRiskResponse,
)
from app.services.gemini_client import GeminiConfigurationError, ask_gemini_async

router = APIRouter(prefix="/api/assistant", tags=["assistant"])

MAX_ROWS = 200
READ_ONLY_PREFIXES = ("SELECT", "WITH")
FORBIDDEN_SQL_KEYWORDS = (
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "TRUNCATE",
    "GRANT",
    "REVOKE",
    "CREATE",
    "MERGE",
    "CALL",
    "COPY",
    "DO",
    "VACUUM",
    "ANALYZE",
)

SQL_SYSTEM_INSTRUCTION = """
Bạn là trợ lý chuyển ngôn ngữ tự nhiên sang SQL PostgreSQL chỉ đọc dữ liệu cho nhân viên sản xuất.

Bảng trong schema public:
- dim_employees(employee_id, employee_name, title, contact_email, contact_phone)
- dim_customers(customer_id, customer_name, contact_phone, contact_email)
- dim_suppliers(supplier_id, supplier_name, contact_phone, contact_email)
- dim_materials(material_id, material_code, material_name, material_type, unit)
- fact_orders(order_id, pds, customer_id, order_date, delivery_date, quantity, order_note, order_status)
- fact_supply_details(supply_detail_id, supplier_id, material_id, quantity, unit_price, request_date, receive_date)

Bảng trong schema corrugating (phải prefix bằng "corrugating."):
- corrugating.dim_machines(machine_id, machine_name, lead_operator_id, machine_status, flute_type)
- corrugating.dim_machine_breakdowns(breakdown_code, description, how_to_handle, expected_downtime_minutes)
- corrugating.fact_production_logs(production_log_id, pds, leader_id, manager_id, operator_id, supervisor_id, machine_id, product_id, start_time, end_time, product_weight, material_weight, log_note, cut_pallet_count, waste_endroll_weight, waste_trim_weight, waste_production_weight, waste_core_weight)
- corrugating.fact_machine_breakdown_logs(breakdown_log_id, pds, supervisor_id, machine_id, breakdown_code, breakdown_time, recovery_time, breakdown_note)
- corrugating.fact_products(product_id, pds, length, width, unit)

QUY TẮC BẮT BUỘC:
- Chỉ trả về DUY NHẤT câu SQL, không giải thích, không markdown, không dấu ```.
- Chỉ được dùng SELECT hoặc WITH...SELECT. Tuyệt đối không INSERT/UPDATE/DELETE/DROP.
- Với câu không phải truy vấn tổng hợp, phải có LIMIT <= 200.
- Nếu câu hỏi không đủ thông tin để tạo SQL hợp lệ, trả về: SELECT NULL WHERE FALSE
"""

RISK_SYSTEM_INSTRUCTION = """
Bạn giải thích ngắn gọn (3-4 câu) bằng tiếng Việt cho quản lý sản xuất,
không dùng thuật ngữ ML, tập trung vào ý nghĩa thực tế và hành động bảo trì nên làm.
"""


def _normalize_model_sql(raw_sql: str) -> str:
    sql = raw_sql.strip()
    if sql.startswith("```"):
        sql = re.sub(r"^```[\w]*\s*", "", sql)
        sql = re.sub(r"\s*```$", "", sql).strip()
    return sql.strip().rstrip(";").strip()


def _validate_read_only_sql(sql: str) -> str:
    upper_sql = sql.upper()

    if not upper_sql.startswith(READ_ONLY_PREFIXES):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Model không sinh ra câu SELECT hợp lệ.",
        )

    if ";" in sql or "--" in sql or "/*" in sql or "*/" in sql:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Câu SQL chứa cú pháp không được phép.",
        )

    for keyword in FORBIDDEN_SQL_KEYWORDS:
        if re.search(rf"\b{keyword}\b", upper_sql):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Câu SQL chứa từ khóa không được phép: {keyword}",
            )

    if "PG_SLEEP" in upper_sql:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Câu SQL chứa hàm không được phép.",
        )

    return sql


@router.post("/ask-sql", response_model=AskSQLResponse)
async def ask_sql(
    payload: AskSQLRequest,
    current_employee=Depends(get_current_employee),
    db: Session = Depends(get_db),
):
    try:
        raw_sql = await ask_gemini_async(payload.question, system_instruction=SQL_SYSTEM_INSTRUCTION)
    except GeminiConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    sql = _validate_read_only_sql(_normalize_model_sql(raw_sql))

    try:
        result = db.execute(text(sql))
        columns = list(result.keys())
        rows = [dict(row._mapping) for row in result.fetchmany(MAX_ROWS)]
        truncated = result.fetchone() is not None
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Lỗi chạy SQL: {exc}",
        ) from exc

    return AskSQLResponse(
        sql=sql,
        columns=columns,
        rows=rows,
        row_count=len(rows),
        truncated=truncated,
    )


@router.post("/explain-risk", response_model=ExplainRiskResponse)
async def explain_risk(
    payload: ExplainRiskRequest,
    current_employee=Depends(get_current_employee),
):
    prompt = f"""
    Máy: {payload.machine_name}
    Số ngày dự kiến trước khi hỏng: {payload.median_days_to_breakdown}
    Điểm rủi ro tương đối: {payload.relative_risk_score}
    """
    try:
        explanation = await ask_gemini_async(prompt, system_instruction=RISK_SYSTEM_INSTRUCTION)
    except GeminiConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    return ExplainRiskResponse(explanation=explanation.strip())
