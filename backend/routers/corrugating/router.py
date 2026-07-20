# routers/corrugating/router.py
from fastapi import APIRouter
from . import machines, production_logs, breakdowns

router = APIRouter(prefix="api/corrugating", tags=["corrugating"])
router.include_router(machines.router)
router.include_router(production_logs.router)
router.include_router(breakdowns.router)