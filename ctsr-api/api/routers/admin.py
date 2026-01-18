"""
Admin Router

API endpoints for admin dashboard and administrative operations.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.db import get_db
from api.models.admin import DashboardStats
from api.services.admin import AdminService
from api.auth import User, UserRole, require_role

router = APIRouter()


@router.get(
    "/dashboard",
    response_model=DashboardStats,
    summary="Get dashboard statistics",
    description="Get comprehensive dashboard statistics including trials, systems, confirmations, and recent activities. Admin access required.",
)
async def get_dashboard(
    db: AsyncSession = Depends(get_db), user: User = Depends(require_role(UserRole.ADMIN))
) -> DashboardStats:
    """
    Get comprehensive dashboard statistics.

    Returns aggregated statistics for:
    - Trials (total, active, with alerts)
    - Systems (total, active, validated, by criticality)
    - Confirmations (total, pending, overdue, completed this month)
    - Validation alerts (total, open, critical, by type)
    - Recent activities (last 10 actions)

    **Requires:** ADMIN role

    **Returns:**
    - Dashboard statistics with all aggregated counts and recent activities
    """
    service = AdminService(db)
    return await service.get_dashboard_stats()
