from pathlib import Path
from backend.sql_executor import SQLExecutor
from backend.app.core.database import get_engine

def init_ml_schema():
    """Initialize ML schema in database."""
    engine = get_engine()
    executor = SQLExecutor(engine)
    executor.init_schema(
        conn=engine.connect(),
        mother_path="backend/SQL/ml",
        schema="ml",
        ordered_list=("create_schema.sql", "tables", "constraints.sql", "functions", "triggers")
    )
    print("ML schema initialized successfully")

if __name__ == "__main__":
    init_ml_schema()
