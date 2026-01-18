"""Pydantic models for lookups/reference data endpoints."""

from typing import List

from pydantic import BaseModel, Field


class SystemCategoryResponse(BaseModel):
    """System category lookup response."""

    category_code: str = Field(..., description="Category code (e.g., EDC, IRT)")
    category_name: str = Field(..., description="Display name")
    default_criticality: str = Field(..., description="Default criticality level")

    model_config = {"from_attributes": True}


class ValidationStatusResponse(BaseModel):
    """Validation status lookup response."""

    status_code: str = Field(..., description="Status code")
    status_name: str = Field(..., description="Display name")
    requires_attention: bool = Field(..., description="Whether this status requires attention")

    model_config = {"from_attributes": True}


class CriticalityResponse(BaseModel):
    """Criticality level lookup response."""

    criticality_code: str = Field(..., description="Criticality code (CRIT, MAJ, STD)")
    criticality_name: str = Field(..., description="Display name")

    model_config = {"from_attributes": True}


class LookupsResponse(BaseModel):
    """Complete lookups/reference data response."""

    system_categories: List[SystemCategoryResponse] = Field(..., description="System category codes")
    validation_statuses: List[ValidationStatusResponse] = Field(..., description="Validation status codes")
    criticality_levels: List[CriticalityResponse] = Field(..., description="Criticality levels")
    vendor_types: List[str] = Field(..., description="Vendor type codes")
    hosting_models: List[str] = Field(..., description="Hosting model codes")
    data_hosting_regions: List[str] = Field(..., description="Data hosting region codes")
