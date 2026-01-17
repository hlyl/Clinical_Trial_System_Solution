"""Lookups/reference data endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.db import get_db
from api.models.lookups import LookupsResponse
from api.services.lookups import LookupsService

router = APIRouter()


@router.get(
    "/lookups",
    response_model=LookupsResponse,
    summary="Get all reference data",
    description="Returns all lookup tables for client-side caching. "
    "Includes system categories, validation statuses, criticality levels, "
    "vendor types, hosting models, and data hosting regions.",
)
async def get_lookups(db: AsyncSession = Depends(get_db)) -> LookupsResponse:
    """
    Fetch all reference/lookup data.
    
    This endpoint returns all lookup tables in a single response for efficient
    client-side caching. No authentication required.
    
    Returns:
        LookupsResponse: All reference data
    """
    return await LookupsService.get_all_lookups(db)
