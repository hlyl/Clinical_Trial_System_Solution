"""Pydantic models for trial management."""

from datetime import date, datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


# Trial Models
class TrialCreate(BaseModel):
    """Request model for creating a trial."""

    protocol_number: str = Field(..., min_length=1, max_length=50, description="Protocol number")
    trial_title: Optional[str] = Field(None, max_length=500, description="Trial title")
    trial_phase: Optional[str] = Field(None, description="Trial phase")
    trial_status: str = Field(default="ACTIVE", description="Trial status")
    therapeutic_area: Optional[str] = Field(None, max_length=100, description="Therapeutic area")
    trial_start_date: Optional[date] = Field(None, description="Trial start date")
    trial_close_date: Optional[date] = Field(None, description="Trial close date")
    trial_lead_name: Optional[str] = Field(None, max_length=200, description="Trial lead name")
    trial_lead_email: Optional[str] = Field(None, max_length=200, description="Trial lead email")
    ctms_trial_id: Optional[str] = Field(None, max_length=100, description="CTMS trial ID")


class TrialUpdate(BaseModel):
    """Request model for updating a trial."""

    trial_title: Optional[str] = Field(None, max_length=500)
    trial_phase: Optional[str] = None
    trial_status: Optional[str] = None
    therapeutic_area: Optional[str] = Field(None, max_length=100)
    trial_start_date: Optional[date] = None
    trial_close_date: Optional[date] = None
    trial_lead_name: Optional[str] = Field(None, max_length=200)
    trial_lead_email: Optional[str] = Field(None, max_length=200)
    ctms_trial_id: Optional[str] = Field(None, max_length=100)
    next_confirmation_due: Optional[date] = None


class TrialResponse(BaseModel):
    """Response model for trial."""

    trial_id: UUID
    protocol_number: str
    trial_title: Optional[str]
    trial_phase: Optional[str]
    trial_status: str
    therapeutic_area: Optional[str]
    trial_start_date: Optional[date]
    trial_close_date: Optional[date]
    trial_lead_name: Optional[str]
    trial_lead_email: Optional[str]
    ctms_trial_id: Optional[str]
    last_ctms_sync: Optional[datetime]
    next_confirmation_due: Optional[date]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Trial-System Link Models
class SystemLinkCreate(BaseModel):
    """Request model for linking a system to a trial."""

    instance_id: UUID = Field(..., description="System instance UUID")
    criticality_code: str = Field(..., description="Criticality level (HIGH/MEDIUM/LOW)")
    criticality_override_reason: Optional[str] = Field(
        None, max_length=500, description="Reason for criticality override"
    )
    usage_start_date: Optional[date] = Field(None, description="Usage start date")
    usage_end_date: Optional[date] = Field(None, description="Usage end date")


class SystemLinkUpdate(BaseModel):
    """Request model for updating a trial-system link."""

    assignment_status: Optional[str] = Field(None, description="Assignment status")
    criticality_code: Optional[str] = Field(None, description="Criticality level")
    criticality_override_reason: Optional[str] = Field(None, max_length=500)
    usage_start_date: Optional[date] = None
    usage_end_date: Optional[date] = None


class SystemLinkResponse(BaseModel):
    """Response model for trial-system link."""

    link_id: UUID
    trial_id: UUID
    instance_id: UUID
    assignment_status: str
    criticality_code: str
    criticality_override_reason: Optional[str]
    usage_start_date: date
    usage_end_date: Optional[date]
    linked_by: Optional[str]
    linked_at: datetime
    unlinked_by: Optional[str]
    unlinked_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LinkedSystemDetail(BaseModel):
    """Detailed information about a linked system."""

    link_id: UUID
    instance_id: UUID
    instance_code: str
    platform_name: str
    category_code: str
    assignment_status: str
    criticality_code: str
    criticality_override_reason: Optional[str]
    usage_start_date: date
    usage_end_date: Optional[date]
    linked_at: datetime

    model_config = {"from_attributes": True}


class TrialDetail(BaseModel):
    """Detailed trial response with linked systems."""

    trial_id: UUID
    protocol_number: str
    trial_title: Optional[str]
    trial_phase: Optional[str]
    trial_status: str
    therapeutic_area: Optional[str]
    trial_start_date: Optional[date]
    trial_close_date: Optional[date]
    trial_lead_name: Optional[str]
    trial_lead_email: Optional[str]
    ctms_trial_id: Optional[str]
    last_ctms_sync: Optional[datetime]
    next_confirmation_due: Optional[date]
    created_at: datetime
    updated_at: datetime
    linked_systems: List[LinkedSystemDetail] = []

    model_config = {"from_attributes": True}


class TrialListResponse(BaseModel):
    """Response model for trial list."""

    data: List[TrialResponse]
    meta: dict
