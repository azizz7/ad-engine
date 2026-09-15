import logging

from fastapi import APIRouter
from sqlalchemy import text

from app.db.session import SessionLocal

router = APIRouter(prefix="/api", tags=["health"])
logger = logging.getLogger(__name__)


@router.get("/health")
async def health_check():
    """Report service + database connectivity status."""
    db_ok = True
    try:
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
        finally:
            db.close()
    except Exception:
        logger.exception("Health check database connectivity failed")
        db_ok = False

    return {"status": "healthy" if db_ok else "degraded", "database": "ok" if db_ok else "unreachable"}
