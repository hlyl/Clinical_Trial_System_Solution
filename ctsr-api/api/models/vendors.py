"""Pydantic models for vendor endpoints."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from api.utils.pagination import PaginationMeta


class VendorCreate(BaseModel):
    """Request model for creating a vendor."""

    vendor_code: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Unique vendor code (e.g., ICON_CRO)",
        pattern="^[A-Z0-9_]+$",
    )
    vendor_name: str = Field(
        ..., min_length=1, max_length=200, description="Display name"
    )
    vendor_type: str = Field(
        ...,
        description="Vendor type",
    )
    contact_name: Optional[str] = Field(
        None, max_length=200, description="Primary contact name"
    )
    contact_email: Optional[str] = Field(
        None, max_length=200, description="Primary contact email"
    )

    @field_validator("vendor_type")
    @classmethod
    def validate_vendor_type(cls, v: str) -> str:
        """Validate vendor type."""
        valid_types = [
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
        if v not in valid_types:
            raise ValueError(f"vendor_type must be one of: {', '.join(valid_types)}")
        return v


class VendorUpdate(BaseModel):
    """Request model for updating a vendor."""

    vendor_name: Optional[str] = Field(
        None, min_length=1, max_length=200, description="Display name"
    )
    vendor_type: Optional[str] = Field(None, description="Vendor type")
    contact_name: Optional[str] = Field(
        None, max_length=200, description="Primary contact name"
    )
    contact_email: Optional[str] = Field(
        None, max_length=200, description="Primary contact email"
    )
    is_active: Optional[bool] = Field(None, description="Active status")

    @field_validator("vendor_type")
    @classmethod
    def validate_vendor_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate vendor type."""
        if v is None:
            return v
        valid_types = [
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
        if v not in valid_types:
            raise ValueError(f"vendor_type must be one of: {', '.join(valid_types)}")
        return v


class VendorResponse(BaseModel):
    """Response model for vendor."""

    vendor_id: UUID = Field(..., description="Vendor unique ID")
    vendor_code: str = Field(..., description="Vendor code")
    vendor_name: str = Field(..., description="Display name")
    vendor_type: str = Field(..., description="Vendor type")
    contact_name: Optional[str] = Field(None, description="Primary contact name")
    contact_email: Optional[str] = Field(None, description="Primary contact email")
    is_active: bool = Field(..., description="Active status")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = {"from_attributes": True}


class VendorListResponse(BaseModel):
    """Response model for vendor list."""

    data: List[VendorResponse] = Field(..., description="List of vendors")
    meta: PaginationMeta = Field(..., description="Pagination metadata")
