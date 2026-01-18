"""System instance management endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth import User, require_admin, require_viewer
from api.db import get_db
from api.models.systems import (
    SystemCreate,
    SystemDetail,
    SystemListResponse,
    SystemResponse,
    SystemUpdate,
)
from api.services.systems import SystemService
from api.utils.pagination import PaginationParams

router = APIRouter()


@router.get(
    "/systems",
    response_model=SystemListResponse,
    summary="List system instances",
    description="Returns a paginated list of system instances with optional filtering and search.",
)
async def list_systems(
    category_code: Optional[str] = Query(None, description="Filter by system category"),
    validation_status: Optional[str] = Query(None, description="Filter by validation status"),
    data_hosting_region: Optional[str] = Query(None, description="Filter by data hosting region"),
    vendor_id: Optional[UUID] = Query(None, description="Filter by vendor (platform or service provider)"),
    is_active: bool = Query(True, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search in instance_code, platform_name, instance_name"),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_viewer),
) -> SystemListResponse:
    """
    List all system instances with pagination, filtering, and search.

    Requires CTSR_VIEWER role or higher.

    Args:
        category_code: Optional filter by category (EDC, IRT, etc.)
        validation_status: Optional filter by validation status
        data_hosting_region: Optional filter by hosting region
        vendor_id: Optional filter by vendor UUID
        is_active: Filter by active status (default: true)
        search: Optional search term
        pagination: Pagination parameters
        db: Database session
        user: Authenticated user

    Returns:
        SystemListResponse: Paginated list of systems
    """
    return await SystemService.list_systems(
        db=db,
        pagination=pagination,
        category_code=category_code,
        validation_status=validation_status,
        data_hosting_region=data_hosting_region,
        vendor_id=vendor_id,
        is_active=is_active,
        search=search,
        user_email=user.email,
    )


@router.post(
    "/systems",
    response_model=SystemResponse,
    status_code=201,
    summary="Create system instance",
    description="Create a new system instance. Requires CTSR_ADMIN role.",
)
async def create_system(
    system_data: SystemCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
) -> SystemResponse:
    """
    Create a new system instance.

    Requires CTSR_ADMIN role.

    Args:
        system_data: System creation data
        db: Database session
        user: Authenticated user

    Returns:
        SystemResponse: Created system

    Raises:
        409 Conflict: If instance_code already exists
        400 Bad Request: If validation fails
    """
    return await SystemService.create_system(
        db=db, system_data=system_data, user_email=user.email
    )


@router.get(
    "/systems/{instance_id}",
    response_model=SystemDetail,
    summary="Get system details",
    description="Returns detailed information about a specific system including linked trials and change history.",
)
async def get_system(
    instance_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_viewer),
) -> SystemDetail:
    """
    Get system by ID with linked trials and audit history.

    Requires CTSR_VIEWER role or higher.

    Args:
        instance_id: System instance UUID
        db: Database session
        user: Authenticated user

    Returns:
        SystemDetail: System details with linked trials and audit history

    Raises:
        404 Not Found: If system doesn't exist
    """
    return await SystemService.get_system(
        db=db, instance_id=instance_id, user_email=user.email
    )


@router.put(
    "/systems/{instance_id}",
    response_model=SystemResponse,
    summary="Update system instance",
    description="Update system instance information. Requires CTSR_ADMIN role.",
)
async def update_system(
    instance_id: UUID,
    system_data: SystemUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
) -> SystemResponse:
    """
    Update system instance.

    Requires CTSR_ADMIN role.

    Args:
        instance_id: System instance UUID
        system_data: Update data
        db: Database session
        user: Authenticated user

    Returns:
        SystemResponse: Updated system

    Raises:
        404 Not Found: If system doesn't exist
        400 Bad Request: If validation fails
    """
    return await SystemService.update_system(
        db=db, instance_id=instance_id, system_data=system_data, user_email=user.email
    )
