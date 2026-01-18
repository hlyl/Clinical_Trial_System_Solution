"""Pydantic models for confirmation management."""

from datetime import date, datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


# Confirmation Models
class ConfirmationCreate(BaseModel):
    """Request model for creating a confirmation."""

    trial_id: UUID = Field(..., description="Trial UUID")
    confirmation_type: str = Field(..., description="Confirmation type (PERIODIC/DB_LOCK)")
    due_date: Optional[date] = Field(None, description="Due date for confirmation")
    notes: Optional[str] = Field(None, description="Additional notes")


class ConfirmationUpdate(BaseModel):
    """Request model for updating a confirmation."""

    due_date: Optional[date] = None
    notes: Optional[str] = None


class ConfirmationSubmit(BaseModel):
    """Request model for submitting a confirmation."""

    notes: Optional[str] = Field(None, description="Confirmation notes")
    capture_snapshots: bool = Field(default=True, description="Capture system snapshots")


class ConfirmationResponse(BaseModel):
    """Response model for confirmation."""

    confirmation_id: UUID
    trial_id: UUID
    confirmation_type: str
    confirmation_status: str
    due_date: Optional[date]
    confirmed_date: Optional[date]
    confirmed_by: Optional[str]
    notes: Optional[str]
    systems_count: Optional[int]
    validation_alerts_count: Optional[int]
    export_generated: bool
    export_id: Optional[UUID]
    created_at: datetime

    model_config = {"from_attributes": True}


class SystemSnapshotSummary(BaseModel):
    """Summary of a system snapshot."""

    snapshot_id: UUID
    instance_id: UUID
    instance_code: str
    platform_name: str
    validation_status_at: Optional[str]
    platform_version_at: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class ConfirmationDetail(BaseModel):
    """Detailed confirmation response with snapshots."""

    confirmation_id: UUID
    trial_id: UUID
    trial_protocol_number: str
    confirmation_type: str
    confirmation_status: str
    due_date: Optional[date]
    confirmed_date: Optional[date]
    confirmed_by: Optional[str]
    notes: Optional[str]
    systems_count: Optional[int]
    validation_alerts_count: Optional[int]
    export_generated: bool
    export_id: Optional[UUID]
    created_at: datetime
    snapshots: List[SystemSnapshotSummary] = []

    model_config = {"from_attributes": True}


class ConfirmationListResponse(BaseModel):
    """Response model for confirmation list."""

    data: List[ConfirmationResponse]
    meta: dict


# Export Models
class ExportRequest(BaseModel):
    """Request model for generating an eTMF export."""

    confirmation_id: UUID = Field(..., description="Confirmation UUID")
    export_format: str = Field(default="PDF", description="Export format (PDF/EXCEL)")
    include_snapshots: bool = Field(default=True, description="Include system snapshots")
    include_validation_details: bool = Field(default=True, description="Include validation details")


class ExportResponse(BaseModel):
    """Response model for export generation."""

    export_id: UUID
    confirmation_id: UUID
    export_format: str
    status: str
    file_name: Optional[str]
    file_size_bytes: Optional[int]
    download_url: Optional[str]
    generated_at: datetime
    expires_at: Optional[datetime]

    model_config = {"from_attributes": True}
