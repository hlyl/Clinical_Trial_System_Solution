"""Service layer for vendor management."""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.db.models import Vendor
from api.exceptions import ConflictError, NotFoundError, ValidationError
from api.models.vendors import (
    VendorCreate,
    VendorListResponse,
    VendorResponse,
    VendorUpdate,
)
from api.utils.pagination import PaginationMeta, PaginationParams

logger = logging.getLogger(__name__)


class VendorService:
    """Service for vendor CRUD operations."""

    @staticmethod
    async def list_vendors(
        db: AsyncSession,
        pagination: PaginationParams,
        vendor_type: Optional[str] = None,
        is_active: bool = True,
        user_email: Optional[str] = None,
    ) -> VendorListResponse:
        """
        List vendors with pagination and filtering.

        Args:
            db: Database session
            pagination: Pagination parameters
            vendor_type: Filter by vendor type
            is_active: Filter by active status
            user_email: User email for audit logging

        Returns:
            VendorListResponse: List of vendors with pagination metadata
        """
        logger.info(f"Listing vendors - user: {user_email}, type: {vendor_type}, active: {is_active}")

        # Build query
        query = select(Vendor)

        # Apply filters
        if vendor_type:
            query = query.where(Vendor.vendor_type == vendor_type)
        if is_active is not None:
            query = query.where(Vendor.is_active == is_active)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering
        query = query.order_by(Vendor.vendor_name).limit(pagination.limit).offset(pagination.offset)

        # Execute query
        result = await db.execute(query)
        vendors = result.scalars().all()

        logger.info(f"Found {total} vendors, returning {len(vendors)} items")

        return VendorListResponse(
            data=[VendorResponse.model_validate(v) for v in vendors],
            meta=PaginationMeta(total=total, limit=pagination.limit, offset=pagination.offset),
        )

    @staticmethod
    async def create_vendor(db: AsyncSession, vendor_data: VendorCreate, user_email: str) -> VendorResponse:
        """
        Create a new vendor.

        Args:
            db: Database session
            vendor_data: Vendor creation data
            user_email: User email for audit

        Returns:
            VendorResponse: Created vendor

        Raises:
            ConflictError: If vendor_code already exists
            ValidationError: If data is invalid
        """
        logger.info(f"Creating vendor {vendor_data.vendor_code} by user {user_email}")

        # Check if vendor_code already exists
        existing = await db.execute(select(Vendor).where(Vendor.vendor_code == vendor_data.vendor_code))
        if existing.scalar_one_or_none():
            raise ConflictError(
                f"Vendor with code '{vendor_data.vendor_code}' already exists",
                details={"vendor_code": vendor_data.vendor_code},
            )

        # Create vendor
        vendor = Vendor(
            vendor_code=vendor_data.vendor_code,
            vendor_name=vendor_data.vendor_name,
            vendor_type=vendor_data.vendor_type,
            contact_name=vendor_data.contact_name,
            contact_email=vendor_data.contact_email,
            is_active=True,
            created_by=user_email,
            updated_by=user_email,
        )

        db.add(vendor)

        try:
            await db.flush()
            await db.refresh(vendor)
            logger.info(f"Created vendor {vendor.vendor_id}")
            return VendorResponse.model_validate(vendor)
        except IntegrityError as e:
            logger.error(f"Database integrity error creating vendor: {str(e)}")
            raise ConflictError(
                "Failed to create vendor due to constraint violation",
                details={"error": str(e)},
            )

    @staticmethod
    async def get_vendor(db: AsyncSession, vendor_id: UUID, user_email: Optional[str] = None) -> VendorResponse:
        """
        Get vendor by ID.

        Args:
            db: Database session
            vendor_id: Vendor UUID
            user_email: User email for audit logging

        Returns:
            VendorResponse: Vendor details

        Raises:
            NotFoundError: If vendor not found
        """
        logger.info(f"Getting vendor {vendor_id} - user: {user_email}")

        result = await db.execute(select(Vendor).where(Vendor.vendor_id == vendor_id))
        vendor = result.scalar_one_or_none()

        if not vendor:
            raise NotFoundError("Vendor", vendor_id)

        return VendorResponse.model_validate(vendor)

    @staticmethod
    async def update_vendor(
        db: AsyncSession, vendor_id: UUID, vendor_data: VendorUpdate, user_email: str
    ) -> VendorResponse:
        """
        Update vendor.

        Args:
            db: Database session
            vendor_id: Vendor UUID
            vendor_data: Update data
            user_email: User email for audit

        Returns:
            VendorResponse: Updated vendor

        Raises:
            NotFoundError: If vendor not found
            ValidationError: If data is invalid
        """
        logger.info(f"Updating vendor {vendor_id} by user {user_email}")

        # Get existing vendor
        result = await db.execute(select(Vendor).where(Vendor.vendor_id == vendor_id))
        vendor = result.scalar_one_or_none()

        if not vendor:
            raise NotFoundError("Vendor", vendor_id)

        # Update fields if provided
        update_data = vendor_data.model_dump(exclude_unset=True)

        if not update_data:
            logger.warning(f"No fields to update for vendor {vendor_id}")
            return VendorResponse.model_validate(vendor)

        for field, value in update_data.items():
            setattr(vendor, field, value)

        vendor.updated_by = user_email

        try:
            await db.flush()
            await db.refresh(vendor)
            logger.info(f"Updated vendor {vendor_id}")
            return VendorResponse.model_validate(vendor)
        except IntegrityError as e:
            logger.error(f"Database integrity error updating vendor: {str(e)}")
            raise ValidationError(
                "Failed to update vendor due to constraint violation",
                details={"error": str(e)},
            )
