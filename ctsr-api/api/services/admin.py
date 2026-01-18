"""
Admin Service

Business logic for admin dashboard statistics and aggregations.
"""

from datetime import datetime, timedelta

from api.db.models import Confirmation, SystemInstance, Trial, TrialSystemLink, ValidationStatus
from api.models.admin import (
    ConfirmationSummary,
    DashboardStats,
    RecentActivity,
    SystemSummary,
    TrialSummary,
    ValidationAlertSummary,
)
from sqlalchemy import and_, case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession


class AdminService:
    """Service for admin operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dashboard_stats(self) -> DashboardStats:
        """
        Get comprehensive dashboard statistics.

        Returns:
            DashboardStats with aggregated counts and recent activities
        """
        # Get trial statistics
        trial_stats = await self._get_trial_stats()

        # Get system statistics
        system_stats = await self._get_system_stats()

        # Get confirmation statistics
        confirmation_stats = await self._get_confirmation_stats()

        # Get validation alert statistics
        alert_stats = await self._get_alert_stats()

        # Get recent activities
        recent_activities = await self._get_recent_activities()

        return DashboardStats(
            trials=trial_stats,
            systems=system_stats,
            confirmations=confirmation_stats,
            validation_alerts=alert_stats,
            recent_activities=recent_activities,
            generated_at=datetime.utcnow(),
        )

    async def _get_trial_stats(self) -> TrialSummary:
        """Get trial summary statistics."""
        # Total trials (excluding closed/cancelled)
        total_result = await self.db.execute(
            select(func.count(Trial.trial_id)).where(Trial.trial_status.notin_(["CLOSED", "CANCELLED"]))
        )
        total_trials = total_result.scalar() or 0

        # Active trials (trials with active systems)
        active_result = await self.db.execute(
            select(func.count(func.distinct(TrialSystemLink.trial_id)))
            .join(SystemInstance, TrialSystemLink.instance_id == SystemInstance.instance_id)
            .where(and_(SystemInstance.is_active == True, TrialSystemLink.assignment_status == "ACTIVE"))
        )
        active_trials = active_result.scalar() or 0

        # Trials with validation alerts (feature not yet implemented)
        trials_with_alerts = 0

        return TrialSummary(
            total_trials=total_trials, active_trials=active_trials, trials_with_alerts=trials_with_alerts
        )

    async def _get_system_stats(self) -> SystemSummary:
        """Get system summary statistics."""
        # Total systems
        total_result = await self.db.execute(select(func.count(SystemInstance.instance_id)))
        total_systems = total_result.scalar() or 0

        # Active systems
        active_result = await self.db.execute(
            select(func.count(SystemInstance.instance_id)).where(SystemInstance.is_active == True)
        )
        active_systems = active_result.scalar() or 0

        # Validated systems
        validated_result = await self.db.execute(
            select(func.count(SystemInstance.instance_id)).where(
                and_(SystemInstance.is_active == True, SystemInstance.validation_status_code == "VALIDATED")
            )
        )
        validated_systems = validated_result.scalar() or 0

        # Systems needing validation
        needing_validation_result = await self.db.execute(
            select(func.count(SystemInstance.instance_id)).where(
                and_(
                    SystemInstance.is_active == True,
                    or_(
                        SystemInstance.validation_status_code == "NOT_VALIDATED",
                        SystemInstance.validation_status_code == "PENDING_VALIDATION",
                    ),
                )
            )
        )
        systems_needing_validation = needing_validation_result.scalar() or 0

        # Systems by criticality
        criticality_result = await self.db.execute(
            select(TrialSystemLink.criticality_code, func.count(TrialSystemLink.link_id))
            .join(SystemInstance, TrialSystemLink.instance_id == SystemInstance.instance_id)
            .where(and_(TrialSystemLink.assignment_status == "ACTIVE", SystemInstance.is_active == True))
            .group_by(TrialSystemLink.criticality_code)
        )
        systems_by_criticality = {row[0]: row[1] for row in criticality_result.all()}

        return SystemSummary(
            total_systems=total_systems,
            active_systems=active_systems,
            validated_systems=validated_systems,
            systems_needing_validation=systems_needing_validation,
            systems_by_criticality=systems_by_criticality,
        )

    async def _get_confirmation_stats(self) -> ConfirmationSummary:
        """Get confirmation summary statistics."""
        # Total confirmations
        total_result = await self.db.execute(select(func.count(Confirmation.confirmation_id)))
        total_confirmations = total_result.scalar() or 0

        # Pending confirmations
        pending_result = await self.db.execute(
            select(func.count(Confirmation.confirmation_id)).where(Confirmation.confirmation_status == "PENDING")
        )
        pending_confirmations = pending_result.scalar() or 0

        # Overdue confirmations
        today = datetime.utcnow().date()
        overdue_result = await self.db.execute(
            select(func.count(Confirmation.confirmation_id)).where(
                and_(Confirmation.confirmation_status == "PENDING", Confirmation.due_date < today)
            )
        )
        overdue_confirmations = overdue_result.scalar() or 0

        # Completed this month
        first_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        completed_result = await self.db.execute(
            select(func.count(Confirmation.confirmation_id)).where(
                and_(Confirmation.confirmation_status == "COMPLETED", Confirmation.confirmed_date >= first_of_month)
            )
        )
        completed_this_month = completed_result.scalar() or 0

        return ConfirmationSummary(
            total_confirmations=total_confirmations,
            pending_confirmations=pending_confirmations,
            overdue_confirmations=overdue_confirmations,
            completed_this_month=completed_this_month,
        )

    async def _get_alert_stats(self) -> ValidationAlertSummary:
        """Get validation alert summary statistics."""
        # ValidationAlert feature not yet implemented - return zeros
        return ValidationAlertSummary(total_alerts=0, open_alerts=0, critical_alerts=0, alerts_by_type={})

    async def _get_recent_activities(self, limit: int = 10) -> list[RecentActivity]:
        """
        Get recent activities across the system.

        Args:
            limit: Maximum number of activities to return

        Returns:
            List of recent activities
        """
        activities = []

        # Get recent trial creations
        trial_result = await self.db.execute(
            select(Trial.trial_id, Trial.protocol_number, Trial.created_at)
            .where(Trial.trial_status.notin_(["CLOSED", "CANCELLED"]))
            .order_by(Trial.created_at.desc())
            .limit(limit)
        )
        for row in trial_result.all():
            # Ensure datetime is naive
            performed_at = row.created_at.replace(tzinfo=None) if row.created_at.tzinfo else row.created_at
            activities.append(
                RecentActivity(
                    activity_type="TRIAL_CREATED",
                    entity_id=str(row.trial_id),
                    entity_name=row.protocol_number,
                    performed_by="system",
                    performed_at=performed_at,
                    details=f"Trial {row.protocol_number} created",
                )
            )

        # Get recent system additions
        system_result = await self.db.execute(
            select(
                SystemInstance.instance_id,
                SystemInstance.instance_code,
                SystemInstance.platform_name,
                SystemInstance.created_by,
                SystemInstance.created_at,
            )
            .where(SystemInstance.is_active == True)
            .order_by(SystemInstance.created_at.desc())
            .limit(limit)
        )
        for row in system_result.all():
            # Ensure datetime is naive
            performed_at = row.created_at.replace(tzinfo=None) if row.created_at.tzinfo else row.created_at
            activities.append(
                RecentActivity(
                    activity_type="SYSTEM_ADDED",
                    entity_id=str(row.instance_id),
                    entity_name=f"{row.instance_code} - {row.platform_name}",
                    performed_by=row.created_by or "system",
                    performed_at=performed_at,
                    details=f"System {row.instance_code} added",
                )
            )

        # Get recent confirmation submissions
        confirmation_result = await self.db.execute(
            select(
                Confirmation.confirmation_id,
                Confirmation.confirmation_type,
                Confirmation.confirmed_by,
                Confirmation.confirmed_date,
                Trial.protocol_number,
            )
            .join(Trial, Confirmation.trial_id == Trial.trial_id)
            .where(Confirmation.confirmation_status == "COMPLETED")
            .order_by(Confirmation.confirmed_date.desc())
            .limit(limit)
        )
        for row in confirmation_result.all():
            # Convert date to datetime for sorting
            performed_at = (
                datetime.combine(row.confirmed_date, datetime.min.time()) if row.confirmed_date else datetime.utcnow()
            )
            activities.append(
                RecentActivity(
                    activity_type="CONFIRMATION_SUBMITTED",
                    entity_id=str(row.confirmation_id),
                    entity_name=f"{row.confirmation_type} - {row.protocol_number}",
                    performed_by=row.confirmed_by or "system",
                    performed_at=performed_at,
                    details=f"{row.confirmation_type} confirmation submitted for {row.protocol_number}",
                )
            )

        # Sort all activities by date and return top N
        activities.sort(key=lambda x: x.performed_at, reverse=True)
        return activities[:limit]
