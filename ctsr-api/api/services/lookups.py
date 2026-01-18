"""Service layer for lookups/reference data."""

from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.db.models import Criticality, SystemCategory, ValidationStatus
from api.models.lookups import (
    CriticalityResponse,
    LookupsResponse,
    SystemCategoryResponse,
    ValidationStatusResponse,
)


class LookupsService:
    """Service for fetching reference/lookup data."""

    @staticmethod
    async def get_all_lookups(db: AsyncSession) -> LookupsResponse:
        """
        Fetch all lookup tables for client-side caching.

        Args:
            db: Database session

        Returns:
            LookupsResponse: All reference data
        """
        # Fetch system categories
        result = await db.execute(
            select(SystemCategory).where(SystemCategory.is_active == True).order_by(SystemCategory.sort_order)
        )
        categories = result.scalars().all()

        # Fetch validation statuses
        result = await db.execute(
            select(ValidationStatus).where(ValidationStatus.is_active == True).order_by(ValidationStatus.sort_order)
        )
        statuses = result.scalars().all()

        # Fetch criticality levels
        result = await db.execute(
            select(Criticality).where(Criticality.is_active == True).order_by(Criticality.sort_order)
        )
        criticalities = result.scalars().all()

        # Static enums (from schema constraints)
        vendor_types = [
            "CRO",
            "FSP",
            "TECH_VENDOR",
            "CENTRAL_LAB",
            "IMAGING",
            "ECG_VENDOR",
            "BIOANALYTICAL",
            "LOGISTICS",
            "SPECIALTY",
            "INTERNAL",
        ]

        hosting_models = [
            "SAAS",
            "SAAS_ST",
            "PAAS",
            "IAAS",
            "ON_PREM",
            "HYBRID",
        ]

        data_hosting_regions = [
            "EU",
            "US",
            "CHINA",
            "APAC_OTHER",
            "UK",
            "GLOBAL_DISTRIBUTED",
        ]

        return LookupsResponse(
            system_categories=[SystemCategoryResponse.model_validate(cat) for cat in categories],
            validation_statuses=[ValidationStatusResponse.model_validate(status) for status in statuses],
            criticality_levels=[CriticalityResponse.model_validate(crit) for crit in criticalities],
            vendor_types=vendor_types,
            hosting_models=hosting_models,
            data_hosting_regions=data_hosting_regions,
        )
