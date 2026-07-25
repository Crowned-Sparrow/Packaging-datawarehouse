from fastapi import APIRouter
from . import machines, production_logs, breakdowns

router = APIRouter(prefix="/corrugating", tags=["Corrugating"])

router.include_router(machines.router, prefix="/machines")
router.include_router(production_logs.router, prefix="/logs")
router.include_router(breakdowns.router, prefix="/breakdowns")
