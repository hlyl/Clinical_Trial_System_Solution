"""Vendor management endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth import User, require_admin, require_viewer
from api.db import get_db
from api.models.vendors import VendorCreate, VendorListResponse, VendorResponse, VendorUpdate
from api.services.vendors import VendorService
from api.utils.pagination import PaginationParams

router = APIRouter()


@router.get(
    "/vendors",
    response_model=VendorListResponse,
    summary="List vendors",
    description="Returns a paginated list of vendors with optional filtering by type and active status.",
)
async def list_vendors(
    vendor_type: Optional[str] = Query(None, description="Filter by vendor type"),
    is_active: bool = Query(True, description="Filter by active status"),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_viewer),
) -> VendorListResponse:
    """
    List all vendors with pagination.

    Requires CTSR_VIEWER role or higher.

    Args:
        vendor_type: Optional filter by vendor type
        is_active: Filter by active status (default: true)
        pagination: Pagination parameters
        db: Database session
        user: Authenticated user

    Returns:
        VendorListResponse: Paginated list of vendors
    """
    return await VendorService.list_vendors(
        db=db,
        pagination=pagination,
        vendor_type=vendor_type,
        is_active=is_active,
        user_email=user.email,
    )


@router.post(
    "/vendors",
    response_model=VendorResponse,
    status_code=201,
    summary="Create vendor",
    description="Create a new vendor. Requires CTSR_ADMIN role.",
)
async def create_vendor(
    vendor_data: VendorCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
) -> VendorResponse:
    """
    Create a new vendor.

    Requires CTSR_ADMIN role.

    Args:
        vendor_data: Vendor creation data
        db: Database session
        user: Authenticated user

    Returns:
        VendorResponse: Created vendor

    Raises:
        409 Conflict: If vendor_code already exists
        400 Bad Request: If validation fails
    """
    return await VendorService.create_vendor(db=db, vendor_data=vendor_data, user_email=user.email)


@router.get(
    "/vendors/{vendor_id}",
    response_model=VendorResponse,
    summary="Get vendor details",
    description="Returns detailed information about a specific vendor.",
)
async def get_vendor(
    vendor_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_viewer),
) -> VendorResponse:
    """
    Get vendor by ID.

    Requires CTSR_VIEWER role or higher.

    Args:
        vendor_id: Vendor UUID
        db: Database session
        user: Authenticated user

    Returns:
        VendorResponse: Vendor details

    Raises:
        404 Not Found: If vendor doesn't exist
    """
    return await VendorService.get_vendor(db=db, vendor_id=vendor_id, user_email=user.email)


@router.put(
    "/vendors/{vendor_id}",
    response_model=VendorResponse,
    summary="Update vendor",
    description="Update vendor information. Requires CTSR_ADMIN role.",
)
async def update_vendor(
    vendor_id: UUID,
    vendor_data: VendorUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
) -> VendorResponse:
    """
    Update vendor.

    Requires CTSR_ADMIN role.

    Args:
        vendor_id: Vendor UUID
        vendor_data: Update data
        db: Database session
        user: Authenticated user

    Returns:
        VendorResponse: Updated vendor

    Raises:
        404 Not Found: If vendor doesn't exist
        400 Bad Request: If validation fails
    """
    return await VendorService.update_vendor(db=db, vendor_id=vendor_id, vendor_data=vendor_data, user_email=user.email)
