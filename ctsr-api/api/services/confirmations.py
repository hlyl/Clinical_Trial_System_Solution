"""Service layer for confirmation management."""

import logging
from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID, uuid4

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from api.db.models import Confirmation, LinkSnapshot, Trial, TrialSystemLink, SystemInstance
from api.models.confirmations import (
    ConfirmationCreate,
    ConfirmationUpdate,
    ConfirmationResponse,
    ConfirmationDetail,
    SystemSnapshotSummary,
    ConfirmationSubmit,
    ExportRequest,
    ExportResponse,
)
from api.exceptions import NotFoundError, ConflictError, ValidationError
from api.utils.pagination import PaginationParams, PaginationMeta

logger = logging.getLogger(__name__)


class ConfirmationService:
    """Service for managing confirmations and exports."""

    @staticmethod
    async def list_confirmations(
        db: AsyncSession,
        pagination: PaginationParams,
        trial_id: Optional[UUID] = None,
        confirmation_status: Optional[str] = None,
        confirmation_type: Optional[str] = None,
        overdue_only: bool = False,
        user_email: str = "system",
    ) -> tuple[List[Confirmation], PaginationMeta]:
        """List confirmations with optional filters."""
        logger.info(
            f"Listing confirmations - user: {user_email}, trial: {trial_id}, "
            f"status: {confirmation_status}, overdue: {overdue_only}"
        )

        # Build base query
        query = select(Confirmation)

        # Apply filters
        if trial_id:
            query = query.where(Confirmation.trial_id == trial_id)
        if confirmation_status:
            query = query.where(Confirmation.confirmation_status == confirmation_status)
        if confirmation_type:
            query = query.where(Confirmation.confirmation_type == confirmation_type)
        if overdue_only:
            query = query.where(
                and_(
                    Confirmation.confirmation_status == "PENDING",
                    Confirmation.due_date < datetime.utcnow().date(),
                )
            )

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        # Apply ordering and pagination
        query = query.order_by(Confirmation.due_date.desc())
        query = query.limit(pagination.limit).offset(pagination.offset)

        # Execute query
        result = await db.execute(query)
        confirmations = result.scalars().all()

        logger.info(f"Found {total} confirmations, returning {len(confirmations)} items")

        return list(confirmations), PaginationMeta(total=total, limit=pagination.limit, offset=pagination.offset)

    @staticmethod
    async def create_confirmation(
        db: AsyncSession, confirmation_data: ConfirmationCreate, user_email: str
    ) -> ConfirmationResponse:
        """Create a new confirmation."""
        logger.info(f"Creating confirmation for trial {confirmation_data.trial_id} by {user_email}")

        # Verify trial exists
        trial_query = select(Trial).where(Trial.trial_id == confirmation_data.trial_id)
        trial_result = await db.execute(trial_query)
        if not trial_result.scalar_one_or_none():
            raise NotFoundError("Trial", confirmation_data.trial_id)

        # Count active systems for this trial
        systems_count_query = select(func.count()).select_from(
            select(TrialSystemLink)
            .where(
                and_(
                    TrialSystemLink.trial_id == confirmation_data.trial_id,
                    TrialSystemLink.unlinked_at.is_(None),
                )
            )
            .subquery()
        )
        systems_count_result = await db.execute(systems_count_query)
        systems_count = systems_count_result.scalar_one()

        # Create confirmation
        confirmation = Confirmation(
            trial_id=confirmation_data.trial_id,
            confirmation_type=confirmation_data.confirmation_type,
            due_date=confirmation_data.due_date,
            notes=confirmation_data.notes,
            systems_count=systems_count,
        )

        try:
            db.add(confirmation)
            await db.commit()
            await db.refresh(confirmation)
            logger.info(f"Confirmation created: {confirmation.confirmation_id}")
            return ConfirmationResponse.model_validate(confirmation)
        except IntegrityError as e:
            await db.rollback()
            logger.error(f"Database integrity error creating confirmation: {e}")
            raise ConflictError("Failed to create confirmation due to constraint violation")

    @staticmethod
    async def get_confirmation(db: AsyncSession, confirmation_id: UUID, user_email: str) -> ConfirmationDetail:
        """Get confirmation details with snapshots."""
        logger.info(f"Fetching confirmation {confirmation_id} for user {user_email}")

        # Get confirmation with trial info
        confirmation_query = (
            select(Confirmation, Trial.protocol_number)
            .join(Trial, Confirmation.trial_id == Trial.trial_id)
            .where(Confirmation.confirmation_id == confirmation_id)
        )
        confirmation_result = await db.execute(confirmation_query)
        result_row = confirmation_result.first()

        if not result_row:
            raise NotFoundError("Confirmation", confirmation_id)

        confirmation, protocol_number = result_row

        # Get snapshots
        snapshots_query = (
            select(
                LinkSnapshot,
                SystemInstance.instance_code,
                SystemInstance.platform_name,
            )
            .join(
                SystemInstance,
                LinkSnapshot.instance_id == SystemInstance.instance_id,
            )
            .where(LinkSnapshot.confirmation_id == confirmation_id)
            .order_by(LinkSnapshot.created_at.desc())
        )

        snapshots_result = await db.execute(snapshots_query)
        snapshots_data = snapshots_result.all()

        # Build snapshots list
        snapshots = []
        for snapshot, instance_code, platform_name in snapshots_data:
            snapshots.append(
                SystemSnapshotSummary(
                    snapshot_id=snapshot.snapshot_id,
                    instance_id=snapshot.instance_id,
                    instance_code=instance_code,
                    platform_name=platform_name,
                    validation_status_at=snapshot.validation_status_at,
                    platform_version_at=snapshot.platform_version_at,
                    created_at=snapshot.created_at,
                )
            )

        # Build response
        confirmation_dict = {
            "confirmation_id": confirmation.confirmation_id,
            "trial_id": confirmation.trial_id,
            "trial_protocol_number": protocol_number,
            "confirmation_type": confirmation.confirmation_type,
            "confirmation_status": confirmation.confirmation_status,
            "due_date": confirmation.due_date,
            "confirmed_date": confirmation.confirmed_date,
            "confirmed_by": confirmation.confirmed_by,
            "notes": confirmation.notes,
            "systems_count": confirmation.systems_count,
            "validation_alerts_count": confirmation.validation_alerts_count,
            "export_generated": confirmation.export_generated,
            "export_id": confirmation.export_id,
            "created_at": confirmation.created_at,
            "snapshots": snapshots,
        }

        return ConfirmationDetail(**confirmation_dict)

    @staticmethod
    async def update_confirmation(
        db: AsyncSession,
        confirmation_id: UUID,
        confirmation_data: ConfirmationUpdate,
        user_email: str,
    ) -> ConfirmationResponse:
        """Update a confirmation."""
        logger.info(f"Updating confirmation {confirmation_id} by {user_email}")

        # Get confirmation
        confirmation_query = select(Confirmation).where(Confirmation.confirmation_id == confirmation_id)
        confirmation_result = await db.execute(confirmation_query)
        confirmation = confirmation_result.scalar_one_or_none()

        if not confirmation:
            raise NotFoundError("Confirmation", confirmation_id)

        # Don't allow updates to completed confirmations
        if confirmation.confirmation_status == "COMPLETED":
            raise ValidationError("Cannot update a completed confirmation")

        # Update fields
        update_data = confirmation_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(confirmation, key, value)

        try:
            await db.commit()
            await db.refresh(confirmation)
            logger.info(f"Confirmation updated: {confirmation_id}")
            return ConfirmationResponse.model_validate(confirmation)
        except IntegrityError as e:
            await db.rollback()
            logger.error(f"Database integrity error updating confirmation: {e}")
            raise ConflictError("Failed to update confirmation due to constraint violation")

    @staticmethod
    async def submit_confirmation(
        db: AsyncSession,
        confirmation_id: UUID,
        submit_data: ConfirmationSubmit,
        user_email: str,
    ) -> ConfirmationResponse:
        """Submit a confirmation and optionally capture system snapshots."""
        logger.info(
            f"Submitting confirmation {confirmation_id} by {user_email}, "
            f"capture_snapshots: {submit_data.capture_snapshots}"
        )

        # Get confirmation
        confirmation_query = select(Confirmation).where(Confirmation.confirmation_id == confirmation_id)
        confirmation_result = await db.execute(confirmation_query)
        confirmation = confirmation_result.scalar_one_or_none()

        if not confirmation:
            raise NotFoundError("Confirmation", confirmation_id)

        # Don't allow re-submission
        if confirmation.confirmation_status == "COMPLETED":
            raise ValidationError("Confirmation has already been submitted")

        # Capture snapshots if requested
        if submit_data.capture_snapshots:
            await ConfirmationService._capture_snapshots(db, confirmation.trial_id, confirmation_id)

        # Update confirmation
        confirmation.confirmation_status = "COMPLETED"
        confirmation.confirmed_date = datetime.utcnow().date()
        confirmation.confirmed_by = user_email
        if submit_data.notes:
            confirmation.notes = (
                f"{confirmation.notes}\n{submit_data.notes}" if confirmation.notes else submit_data.notes
            )

        # Count validation alerts
        validation_alerts_query = select(func.count()).select_from(
            select(TrialSystemLink)
            .join(
                SystemInstance,
                TrialSystemLink.instance_id == SystemInstance.instance_id,
            )
            .where(
                and_(
                    TrialSystemLink.trial_id == confirmation.trial_id,
                    TrialSystemLink.unlinked_at.is_(None),
                    SystemInstance.validation_status_code.in_(["VAL_EXPIRED", "NOT_VALIDATED"]),
                )
            )
            .subquery()
        )
        alerts_result = await db.execute(validation_alerts_query)
        confirmation.validation_alerts_count = alerts_result.scalar_one()

        try:
            await db.commit()
            await db.refresh(confirmation)
            logger.info(
                f"Confirmation submitted: {confirmation_id}, " f"alerts: {confirmation.validation_alerts_count}"
            )
            return ConfirmationResponse.model_validate(confirmation)
        except IntegrityError as e:
            await db.rollback()
            logger.error(f"Database integrity error submitting confirmation: {e}")
            raise ConflictError("Failed to submit confirmation due to constraint violation")

    @staticmethod
    async def _capture_snapshots(db: AsyncSession, trial_id: UUID, confirmation_id: UUID) -> None:
        """Capture point-in-time snapshots of trial systems."""
        logger.info(f"Capturing snapshots for trial {trial_id}, confirmation {confirmation_id}")

        # Get active trial-system links
        links_query = (
            select(TrialSystemLink, SystemInstance)
            .join(
                SystemInstance,
                TrialSystemLink.instance_id == SystemInstance.instance_id,
            )
            .where(
                and_(
                    TrialSystemLink.trial_id == trial_id,
                    TrialSystemLink.unlinked_at.is_(None),
                )
            )
        )

        links_result = await db.execute(links_query)
        links_data = links_result.all()

        # Create snapshots
        for link, system in links_data:
            snapshot = LinkSnapshot(
                confirmation_id=confirmation_id,
                link_id=link.link_id,
                instance_id=system.instance_id,
                instance_state={
                    "instance_code": system.instance_code,
                    "platform_name": system.platform_name,
                    "platform_version": system.platform_version,
                    "category_code": system.category_code,
                    "validation_status_code": system.validation_status_code,
                    "validation_date": str(system.validation_date) if system.validation_date else None,
                    "validation_expiry": str(system.validation_expiry) if system.validation_expiry else None,
                    "hosting_model": system.hosting_model,
                    "data_hosting_region": system.data_hosting_region,
                    "criticality_code": link.criticality_code,
                    "assignment_status": link.assignment_status,
                },
                validation_status_at=system.validation_status_code,
                platform_version_at=system.platform_version,
            )
            db.add(snapshot)

        logger.info(f"Created {len(links_data)} snapshots")

    @staticmethod
    async def generate_export(db: AsyncSession, export_request: ExportRequest, user_email: str) -> ExportResponse:
        """Generate an eTMF export for a confirmation."""
        logger.info(
            f"Generating {export_request.export_format} export for confirmation "
            f"{export_request.confirmation_id} by {user_email}"
        )

        # Get confirmation
        confirmation_query = select(Confirmation).where(Confirmation.confirmation_id == export_request.confirmation_id)
        confirmation_result = await db.execute(confirmation_query)
        confirmation = confirmation_result.scalar_one_or_none()

        if not confirmation:
            raise NotFoundError("Confirmation", export_request.confirmation_id)

        # Check if confirmation is completed
        if confirmation.confirmation_status != "COMPLETED":
            raise ValidationError("Can only export completed confirmations")

        # Generate export (simulated for now - in production would generate actual file)
        export_id = uuid4()
        file_name = f"confirmation_{confirmation.confirmation_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{export_request.export_format.lower()}"

        # Update confirmation with export info
        confirmation.export_generated = True
        confirmation.export_id = export_id

        await db.commit()

        # Build export response (simulated)
        export_response = ExportResponse(
            export_id=export_id,
            confirmation_id=confirmation.confirmation_id,
            export_format=export_request.export_format,
            status="COMPLETED",
            file_name=file_name,
            file_size_bytes=1024 * 500,  # Simulated 500KB
            download_url=f"/api/v1/exports/{export_id}/download",
            generated_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=30),
        )

        logger.info(f"Export generated: {export_id}, file: {file_name}")
        return export_response
