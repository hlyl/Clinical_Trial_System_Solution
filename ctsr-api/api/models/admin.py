"""
Admin Dashboard Models

Pydantic models for admin dashboard statistics and aggregated data.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class TrialSummary(BaseModel):
    """Summary statistics for trials."""

    total_trials: int = Field(..., description="Total number of trials")
    active_trials: int = Field(..., description="Trials with active systems")
    trials_with_alerts: int = Field(..., description="Trials with validation alerts")


class SystemSummary(BaseModel):
    """Summary statistics for systems."""

    total_systems: int = Field(..., description="Total system instances")
    active_systems: int = Field(..., description="Active system instances")
    validated_systems: int = Field(..., description="Systems with VALIDATED status")
    systems_needing_validation: int = Field(..., description="Systems needing validation")
    systems_by_criticality: dict[str, int] = Field(..., description="System count by criticality")


class ConfirmationSummary(BaseModel):
    """Summary statistics for confirmations."""

    total_confirmations: int = Field(..., description="Total confirmations")
    pending_confirmations: int = Field(..., description="Pending confirmations")
    overdue_confirmations: int = Field(..., description="Overdue confirmations")
    completed_this_month: int = Field(..., description="Confirmations completed this month")


class ValidationAlertSummary(BaseModel):
    """Summary statistics for validation alerts."""

    total_alerts: int = Field(..., description="Total validation alerts")
    open_alerts: int = Field(..., description="Open validation alerts")
    critical_alerts: int = Field(..., description="Critical severity alerts")
    alerts_by_type: dict[str, int] = Field(..., description="Alert count by type")


class RecentActivity(BaseModel):
    """Recent activity item."""

    activity_type: str = Field(
        ..., description="Type of activity (TRIAL_CREATED, SYSTEM_ADDED, CONFIRMATION_SUBMITTED, etc)"
    )
    entity_id: str = Field(..., description="ID of the entity")
    entity_name: str = Field(..., description="Name or description of entity")
    performed_by: str = Field(..., description="User who performed the action")
    performed_at: datetime = Field(..., description="When the action was performed")
    details: Optional[str] = Field(None, description="Additional details")


class DashboardStats(BaseModel):
    """Comprehensive dashboard statistics."""

    trials: TrialSummary
    systems: SystemSummary
    confirmations: ConfirmationSummary
    validation_alerts: ValidationAlertSummary
    recent_activities: List[RecentActivity] = Field(..., description="Recent activities (last 10)")
    generated_at: datetime = Field(..., description="When these statistics were generated")
