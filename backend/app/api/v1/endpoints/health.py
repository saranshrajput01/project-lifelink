"""
Health check endpoint — used by Docker, load balancers, and monitoring tools.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db

router = APIRouter(tags=["Health"])
settings = get_settings()


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    System health check — verifies database connectivity.
    Returns service status for monitoring dashboards.
    """
    try:
        await db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"

    return {
        "status": "ok" if db_status == "healthy" else "degraded",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_status,
    }
