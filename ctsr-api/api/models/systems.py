"""Pydantic models for system instance endpoints."""

from datetime import date, datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from api.utils.pagination import PaginationMeta
from pydantic import BaseModel, Field


class InterfaceModel(BaseModel):
    """Model for system interface."""

    system_name: str = Field(..., description="Connected system name")
    direction: str = Field(..., description="INBOUND, OUTBOUND, or BIDIRECTIONAL")
    data_type: Optional[str] = Field(None, description="Type of data exchanged")


class MajorChangeModel(BaseModel):
    """Model for major changes."""

    change_date: date = Field(..., description="Change date", alias="date")
    change_description: str = Field(..., description="Change description", alias="description")

    model_config = {"populate_by_name": True}


class SystemCreate(BaseModel):
    """Request model for creating a system instance."""

    instance_code: str = Field(
        ...,
        min_length=5,
        max_length=100,
        description="Unique instance code",
        pattern="^[a-zA-Z0-9_\\-]+$",
    )
    platform_vendor_id: Optional[UUID] = Field(None, description="Platform vendor UUID")
    service_provider_id: Optional[UUID] = Field(None, description="Service provider UUID")
    category_code: str = Field(..., description="System category code")
    platform_name: str = Field(..., min_length=1, max_length=200, description="Platform name")
    platform_version: Optional[str] = Field(None, max_length=50, description="Platform version")
    instance_name: Optional[str] = Field(None, max_length=200, description="Instance name")
    instance_environment: str = Field(default="PRODUCTION", description="Environment type")
    validation_status_code: str = Field(..., description="Validation status code")
    validation_date: Optional[date] = Field(None, description="Validation date")
    validation_expiry: Optional[date] = Field(None, description="Validation expiry date")
    validation_evidence_link: Optional[str] = Field(None, max_length=500, description="Evidence link")
    hosting_model: Optional[str] = Field(None, description="Hosting model")
    data_hosting_region: Optional[str] = Field(None, description="Data hosting region")
    description: Optional[str] = Field(None, description="System description")
    supported_studies: Optional[List[str]] = Field(None, description="List of protocol IDs")
    interfaces: Optional[List[InterfaceModel]] = Field(None, description="System interfaces")
    part11_compliant: Optional[bool] = Field(None, description="21 CFR Part 11 compliant")
    annex11_compliant: Optional[bool] = Field(None, description="EU Annex 11 compliant")
    soc2_certified: Optional[bool] = Field(None, description="SOC 2 certified")
    iso27001_certified: Optional[bool] = Field(None, description="ISO 27001 certified")
    last_major_change_date: Optional[date] = Field(None, description="Last change date")
    last_major_change_desc: Optional[str] = Field(None, max_length=500, description="Last change description")
    next_planned_change_date: Optional[date] = Field(None, description="Next planned change date")
    next_planned_change_desc: Optional[str] = Field(None, max_length=500, description="Next planned change description")


class SystemUpdate(BaseModel):
    """Request model for updating a system instance."""

    platform_vendor_id: Optional[UUID] = None
    service_provider_id: Optional[UUID] = None
    category_code: Optional[str] = None
    platform_name: Optional[str] = Field(None, min_length=1, max_length=200)
    platform_version: Optional[str] = Field(None, max_length=50)
    instance_name: Optional[str] = Field(None, max_length=200)
    instance_environment: Optional[str] = None
    validation_status_code: Optional[str] = None
    validation_date: Optional[date] = None
    validation_expiry: Optional[date] = None
    validation_evidence_link: Optional[str] = Field(None, max_length=500)
    hosting_model: Optional[str] = None
    data_hosting_region: Optional[str] = None
    description: Optional[str] = None
    supported_studies: Optional[List[str]] = None
    interfaces: Optional[List[InterfaceModel]] = None
    part11_compliant: Optional[bool] = None
    annex11_compliant: Optional[bool] = None
    soc2_certified: Optional[bool] = None
    iso27001_certified: Optional[bool] = None
    last_major_change_date: Optional[date] = None
    last_major_change_desc: Optional[str] = Field(None, max_length=500)
    next_planned_change_date: Optional[date] = None
    next_planned_change_desc: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None


class SystemResponse(BaseModel):
    """Response model for system instance."""

    instance_id: UUID
    instance_code: str
    platform_vendor_id: Optional[UUID]
    service_provider_id: Optional[UUID]
    category_code: str
    platform_name: str
    platform_version: Optional[str]
    instance_name: Optional[str]
    instance_environment: str
    validation_status_code: str
    validation_date: Optional[date]
    validation_expiry: Optional[date]
    validation_evidence_link: Optional[str]
    hosting_model: Optional[str]
    data_hosting_region: Optional[str]
    description: Optional[str]
    supported_studies: Optional[List[str]]
    interfaces: Optional[List[InterfaceModel]]
    part11_compliant: Optional[bool]
    annex11_compliant: Optional[bool]
    soc2_certified: Optional[bool]
    iso27001_certified: Optional[bool]
    last_major_change_date: Optional[date]
    last_major_change_desc: Optional[str]
    next_planned_change_date: Optional[date]
    next_planned_change_desc: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AuditRecord(BaseModel):
    """Audit trail record for system changes."""

    audit_id: UUID
    action: str
    changed_at: datetime
    changed_by: Optional[str]
    old_values: Optional[Dict[str, Any]]
    new_values: Optional[Dict[str, Any]]

    model_config = {"from_attributes": True}


class TrialLinkSummary(BaseModel):
    """Summary of trial linkage."""

    trial_id: UUID
    protocol_number: str
    trial_title: str
    criticality_code: str
    assignment_status: str


class SystemDetail(SystemResponse):
    """Detailed system response with linked trials and audit history."""

    linked_trials: List[TrialLinkSummary] = Field(default_factory=list, description="Linked trials")
    audit_history: List[AuditRecord] = Field(default_factory=list, description="Change history")


class SystemListResponse(BaseModel):
    """Response model for system list."""

    data: List[SystemResponse]
    meta: PaginationMeta
