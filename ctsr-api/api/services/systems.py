"""Service layer for system instance management."""

import logging
from datetime import date, datetime
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.db.models import SystemInstance, SystemInstanceAudit, Trial, TrialSystemLink
from api.exceptions import ConflictError, NotFoundError, ValidationError
from api.models.systems import (
    AuditRecord,
    InterfaceModel,
    SystemCreate,
    SystemDetail,
    SystemListResponse,
    SystemResponse,
    SystemUpdate,
    TrialLinkSummary,
)
from api.utils.pagination import PaginationMeta, PaginationParams

logger = logging.getLogger(__name__)


class SystemService:
    """Service for system instance CRUD operations."""

    @staticmethod
    def _serialize_for_audit(value: Any) -> Any:
        """Convert values to JSON-serializable forms for audit storage."""
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        if isinstance(value, UUID):
            return str(value)
        if isinstance(value, list):
            return [SystemService._serialize_for_audit(v) for v in value]
        if isinstance(value, dict):
            return {
                k: SystemService._serialize_for_audit(v) for k, v in value.items()
            }
        return value

    @staticmethod
    async def _record_audit(
        db: AsyncSession,
        instance_id: UUID,
        action: str,
        changed_by: str,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Persist an audit record for a system instance change."""
        record = SystemInstanceAudit(
            instance_id=instance_id,
            action=action,
            changed_by=changed_by,
            old_values={
                k: SystemService._serialize_for_audit(v) for k, v in (old_values or {}).items()
            }
            or None,
            new_values={
                k: SystemService._serialize_for_audit(v) for k, v in (new_values or {}).items()
            }
            or None,
        )
        db.add(record)
        await db.flush()

    @staticmethod
    async def list_systems(
        db: AsyncSession,
        pagination: PaginationParams,
        category_code: Optional[str] = None,
        validation_status: Optional[str] = None,
        data_hosting_region: Optional[str] = None,
        vendor_id: Optional[UUID] = None,
        is_active: bool = True,
        search: Optional[str] = None,
        user_email: Optional[str] = None,
    ) -> SystemListResponse:
        """
        List system instances with pagination, filtering, and search.

        Args:
            db: Database session
            pagination: Pagination parameters
            category_code: Filter by category
            validation_status: Filter by validation status
            data_hosting_region: Filter by hosting region
            vendor_id: Filter by platform vendor or service provider
            is_active: Filter by active status
            search: Search in instance_code, platform_name, instance_name
            user_email: User email for audit logging

        Returns:
            SystemListResponse: List of systems with pagination metadata
        """
        logger.info(
            f"Listing systems - user: {user_email}, search: {search}, "
            f"category: {category_code}, status: {validation_status}"
        )

        # Build query
        query = select(SystemInstance)

        # Apply filters
        if category_code:
            query = query.where(SystemInstance.category_code == category_code)
        if validation_status:
            query = query.where(SystemInstance.validation_status_code == validation_status)
        if data_hosting_region:
            query = query.where(SystemInstance.data_hosting_region == data_hosting_region)
        if vendor_id:
            query = query.where(
                or_(
                    SystemInstance.platform_vendor_id == vendor_id,
                    SystemInstance.service_provider_id == vendor_id,
                )
            )
        if is_active is not None:
            query = query.where(SystemInstance.is_active == is_active)

        # Apply search
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    SystemInstance.instance_code.ilike(search_pattern),
                    SystemInstance.platform_name.ilike(search_pattern),
                    SystemInstance.instance_name.ilike(search_pattern),
                )
            )

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering
        query = (
            query.order_by(SystemInstance.instance_code)
            .limit(pagination.limit)
            .offset(pagination.offset)
        )

        # Execute query
        result = await db.execute(query)
        systems = result.scalars().all()

        logger.info(f"Found {total} systems, returning {len(systems)} items")

        return SystemListResponse(
            data=[SystemResponse.model_validate(s) for s in systems],
            meta=PaginationMeta(
                total=total, limit=pagination.limit, offset=pagination.offset
            ),
        )

    @staticmethod
    async def create_system(
        db: AsyncSession, system_data: SystemCreate, user_email: str
    ) -> SystemResponse:
        """
        Create a new system instance.

        Args:
            db: Database session
            system_data: System creation data
            user_email: User email for audit

        Returns:
            SystemResponse: Created system

        Raises:
            ConflictError: If instance_code already exists
            ValidationError: If data is invalid
        """
        logger.info(f"Creating system {system_data.instance_code} by user {user_email}")

        # Check if instance_code already exists
        existing = await db.execute(
            select(SystemInstance).where(
                SystemInstance.instance_code == system_data.instance_code
            )
        )
        if existing.scalar_one_or_none():
            raise ConflictError(
                f"System with code '{system_data.instance_code}' already exists",
                details={"instance_code": system_data.instance_code},
            )

        # Convert interfaces to JSONB format
        interfaces_json = None
        if system_data.interfaces:
            interfaces_json = [interface.model_dump() for interface in system_data.interfaces]

        # Create system instance
        system = SystemInstance(
            instance_code=system_data.instance_code,
            platform_vendor_id=system_data.platform_vendor_id,
            service_provider_id=system_data.service_provider_id,
            category_code=system_data.category_code,
            platform_name=system_data.platform_name,
            platform_version=system_data.platform_version,
            instance_name=system_data.instance_name,
            instance_environment=system_data.instance_environment,
            validation_status_code=system_data.validation_status_code,
            validation_date=system_data.validation_date,
            validation_expiry=system_data.validation_expiry,
            validation_evidence_link=system_data.validation_evidence_link,
            hosting_model=system_data.hosting_model,
            data_hosting_region=system_data.data_hosting_region,
            description=system_data.description,
            supported_studies=system_data.supported_studies,
            interfaces=interfaces_json,
            part11_compliant=system_data.part11_compliant,
            annex11_compliant=system_data.annex11_compliant,
            soc2_certified=system_data.soc2_certified,
            iso27001_certified=system_data.iso27001_certified,
            last_major_change_date=system_data.last_major_change_date,
            last_major_change_desc=system_data.last_major_change_desc,
            next_planned_change_date=system_data.next_planned_change_date,
            next_planned_change_desc=system_data.next_planned_change_desc,
            is_active=True,
            created_by=user_email,
            updated_by=user_email,
        )

        db.add(system)

        try:
            await db.flush()
            await db.refresh(system)
            await SystemService._record_audit(
                db=db,
                instance_id=system.instance_id,
                action="CREATE",
                changed_by=user_email,
                old_values=None,
                new_values=SystemResponse.model_validate(system).model_dump(),
            )
            logger.info(f"Created system {system.instance_id}")
            return SystemResponse.model_validate(system)
        except IntegrityError as e:
            logger.error(f"Database integrity error creating system: {str(e)}")
            raise ConflictError(
                "Failed to create system due to constraint violation",
                details={"error": str(e)},
            )

    @staticmethod
    async def get_system(
        db: AsyncSession, instance_id: UUID, user_email: Optional[str] = None
    ) -> SystemDetail:
        """
        Get system by ID with linked trials and audit history.

        Args:
            db: Database session
            instance_id: System instance UUID
            user_email: User email for audit logging

        Returns:
            SystemDetail: System details with linked trials and audit history

        Raises:
            NotFoundError: If system not found
        """
        logger.info(f"Getting system {instance_id} - user: {user_email}")

        # Get system instance
        result = await db.execute(
            select(SystemInstance).where(SystemInstance.instance_id == instance_id)
        )
        system = result.scalar_one_or_none()

        if not system:
            raise NotFoundError("System", instance_id)

        # Get linked trials
        trials_result = await db.execute(
            select(TrialSystemLink, Trial)
            .join(Trial, TrialSystemLink.trial_id == Trial.trial_id)
            .where(TrialSystemLink.instance_id == instance_id)
            .where(TrialSystemLink.assignment_status.in_(["ACTIVE", "CONFIRMED"]))
        )
        trials_data = trials_result.all()

        linked_trials = [
            TrialLinkSummary(
                trial_id=trial.trial_id,
                protocol_number=trial.protocol_number,
                trial_title=trial.trial_title,
                criticality_code=link.criticality_code,
                assignment_status=link.assignment_status,
            )
            for link, trial in trials_data
        ]

        # Get audit history (last 20 changes)
        audit_result = await db.execute(
            select(SystemInstanceAudit)
            .where(SystemInstanceAudit.instance_id == instance_id)
            .order_by(SystemInstanceAudit.changed_at.desc())
            .limit(20)
        )
        audit_records = audit_result.scalars().all()

        audit_history = [AuditRecord.model_validate(record) for record in audit_records]

        # Build detail response
        system_dict = SystemResponse.model_validate(system).model_dump()
        return SystemDetail(
            **system_dict,
            linked_trials=linked_trials,
            audit_history=audit_history,
        )

    @staticmethod
    async def update_system(
        db: AsyncSession, instance_id: UUID, system_data: SystemUpdate, user_email: str
    ) -> SystemResponse:
        """
        Update system instance.

        Args:
            db: Database session
            instance_id: System instance UUID
            system_data: Update data
            user_email: User email for audit

        Returns:
            SystemResponse: Updated system

        Raises:
            NotFoundError: If system not found
            ValidationError: If data is invalid
        """
        logger.info(f"Updating system {instance_id} by user {user_email}")

        # Get existing system
        result = await db.execute(
            select(SystemInstance).where(SystemInstance.instance_id == instance_id)
        )
        system = result.scalar_one_or_none()

        if not system:
            raise NotFoundError("System", instance_id)

        # Capture state before changes for auditing
        old_snapshot = SystemResponse.model_validate(system).model_dump()

        # Update fields if provided
        update_data = system_data.model_dump(exclude_unset=True)

        if not update_data:
            logger.warning(f"No fields to update for system {instance_id}")
            return SystemResponse.model_validate(system)

        # Handle interfaces conversion
        if "interfaces" in update_data and update_data["interfaces"] is not None:
            if isinstance(update_data["interfaces"], list):
                update_data["interfaces"] = [
                    interface.model_dump() if isinstance(interface, InterfaceModel) else interface
                    for interface in update_data["interfaces"]
                ]

        for field, value in update_data.items():
            setattr(system, field, value)

        system.updated_by = user_email

        try:
            await db.flush()
            await db.refresh(system)

            # Compute changed fields for audit trail
            new_snapshot = SystemResponse.model_validate(system).model_dump()
            changed_keys = {
                key
                for key, new_value in new_snapshot.items()
                if old_snapshot.get(key) != new_value
            }

            if changed_keys:
                await SystemService._record_audit(
                    db=db,
                    instance_id=instance_id,
                    action="UPDATE",
                    changed_by=user_email,
                    old_values={k: old_snapshot[k] for k in changed_keys if k in old_snapshot},
                    new_values={k: new_snapshot[k] for k in changed_keys},
                )

            logger.info(f"Updated system {instance_id}")
            return SystemResponse.model_validate(system)
        except IntegrityError as e:
            logger.error(f"Database integrity error updating system: {str(e)}")
            raise ValidationError(
                "Failed to update system due to constraint violation",
                details={"error": str(e)},
            )
