"""Health check endpoint."""

from datetime import datetime
from enum import Enum

from api.db import get_db
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


class HealthStatus(str, Enum):
    """Health status values."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthResponse(BaseModel):
    """Health check response model."""

    status: HealthStatus
    database: str
    timestamp: datetime


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Service health and readiness",
    description="Check the health status of the API and its dependencies. No authentication required.",
)
async def get_health(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    """
    Check service health and database connectivity.

    Returns:
        HealthResponse: Health status information
    """
    # Test database connection
    try:
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        db_status = "connected"
        overall_status = HealthStatus.HEALTHY
    except Exception as e:
        db_status = f"error: {str(e)}"
        overall_status = HealthStatus.UNHEALTHY

    return HealthResponse(
        status=overall_status,
        database=db_status,
        timestamp=datetime.utcnow(),
    )
