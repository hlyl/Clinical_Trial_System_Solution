"""Service layer for trial management."""

import logging
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from api.db.models import Trial, TrialSystemLink, SystemInstance
from api.models.trials import (
    TrialCreate,
    TrialUpdate,
    TrialResponse,
    TrialDetail,
    LinkedSystemDetail,
    SystemLinkCreate,
    SystemLinkUpdate,
    SystemLinkResponse,
)
from api.exceptions import NotFoundError, ConflictError
from api.utils.pagination import PaginationParams, PaginationMeta

logger = logging.getLogger(__name__)


class TrialService:
    """Service for managing trials and trial-system links."""

    @staticmethod
    async def list_trials(
        db: AsyncSession,
        pagination: PaginationParams,
        search: Optional[str] = None,
        trial_status: Optional[str] = None,
        trial_phase: Optional[str] = None,
        therapeutic_area: Optional[str] = None,
        trial_lead_email: Optional[str] = None,
        user_email: str = "system",
    ) -> tuple[List[Trial], PaginationMeta]:
        """List trials with optional filters."""
        logger.info(
            f"Listing trials - user: {user_email}, search: {search}, "
            f"status: {trial_status}, phase: {trial_phase}"
        )

        # Build base query
        query = select(Trial)

        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Trial.protocol_number.ilike(search_term),
                    Trial.trial_title.ilike(search_term),
                    Trial.therapeutic_area.ilike(search_term),
                )
            )

        # Apply filters
        if trial_status:
            query = query.where(Trial.trial_status == trial_status)
        if trial_phase:
            query = query.where(Trial.trial_phase == trial_phase)
        if therapeutic_area:
            query = query.where(Trial.therapeutic_area.ilike(f"%{therapeutic_area}%"))
        if trial_lead_email:
            query = query.where(Trial.trial_lead_email == trial_lead_email)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        # Apply ordering and pagination
        query = query.order_by(Trial.protocol_number)
        query = query.limit(pagination.limit).offset(pagination.offset)

        # Execute query
        result = await db.execute(query)
        trials = result.scalars().all()

        logger.info(f"Found {total} trials, returning {len(trials)} items")

        return list(trials), PaginationMeta(
            total=total, limit=pagination.limit, offset=pagination.offset
        )

    @staticmethod
    async def create_trial(
        db: AsyncSession, trial_data: TrialCreate, user_email: str
    ) -> TrialResponse:
        """Create a new trial."""
        logger.info(f"Creating trial: {trial_data.protocol_number} by {user_email}")

        # Check for duplicate protocol number
        existing_query = select(Trial).where(
            Trial.protocol_number == trial_data.protocol_number
        )
        existing_result = await db.execute(existing_query)
        if existing_result.scalar_one_or_none():
            raise ConflictError(
                f"Trial with protocol '{trial_data.protocol_number}' already exists"
            )

        # Create trial
        trial = Trial(**trial_data.model_dump())

        try:
            db.add(trial)
            await db.commit()
            await db.refresh(trial)
            logger.info(f"Trial created: {trial.trial_id}")
            return TrialResponse.model_validate(trial)
        except IntegrityError as e:
            await db.rollback()
            logger.error(f"Database integrity error creating trial: {e}")
            raise ConflictError("Failed to create trial due to constraint violation")

    @staticmethod
    async def get_trial(db: AsyncSession, trial_id: UUID, user_email: str) -> TrialDetail:
        """Get trial details with linked systems."""
        logger.info(f"Fetching trial {trial_id} for user {user_email}")

        # Get trial
        trial_query = select(Trial).where(Trial.trial_id == trial_id)
        trial_result = await db.execute(trial_query)
        trial = trial_result.scalar_one_or_none()

        if not trial:
            raise NotFoundError("Trial", trial_id)

        # Get linked systems
        links_query = (
            select(
                TrialSystemLink,
                SystemInstance.instance_code,
                SystemInstance.platform_name,
                SystemInstance.category_code,
            )
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
            .order_by(TrialSystemLink.linked_at.desc())
        )

        links_result = await db.execute(links_query)
        links_data = links_result.all()

        # Build linked systems list
        linked_systems = []
        for link, instance_code, platform_name, category_code in links_data:
            linked_systems.append(
                LinkedSystemDetail(
                    link_id=link.link_id,
                    instance_id=link.instance_id,
                    instance_code=instance_code,
                    platform_name=platform_name,
                    category_code=category_code,
                    assignment_status=link.assignment_status,
                    criticality_code=link.criticality_code,
                    criticality_override_reason=link.criticality_override_reason,
                    usage_start_date=link.usage_start_date,
                    usage_end_date=link.usage_end_date,
                    linked_at=link.linked_at,
                )
            )

        # Build response
        trial_dict = {
            "trial_id": trial.trial_id,
            "protocol_number": trial.protocol_number,
            "trial_title": trial.trial_title,
            "trial_phase": trial.trial_phase,
            "trial_status": trial.trial_status,
            "therapeutic_area": trial.therapeutic_area,
            "trial_start_date": trial.trial_start_date,
            "trial_close_date": trial.trial_close_date,
            "trial_lead_name": trial.trial_lead_name,
            "trial_lead_email": trial.trial_lead_email,
            "ctms_trial_id": trial.ctms_trial_id,
            "last_ctms_sync": trial.last_ctms_sync,
            "next_confirmation_due": trial.next_confirmation_due,
            "created_at": trial.created_at,
            "updated_at": trial.updated_at,
            "linked_systems": linked_systems,
        }

        return TrialDetail(**trial_dict)

    @staticmethod
    async def update_trial(
        db: AsyncSession, trial_id: UUID, trial_data: TrialUpdate, user_email: str
    ) -> TrialResponse:
        """Update a trial."""
        logger.info(f"Updating trial {trial_id} by {user_email}")

        # Get trial
        trial_query = select(Trial).where(Trial.trial_id == trial_id)
        trial_result = await db.execute(trial_query)
        trial = trial_result.scalar_one_or_none()

        if not trial:
            raise NotFoundError("Trial", trial_id)

        # Update fields
        update_data = trial_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(trial, key, value)

        trial.updated_at = datetime.utcnow()

        try:
            await db.commit()
            await db.refresh(trial)
            logger.info(f"Trial updated: {trial_id}")
            return TrialResponse.model_validate(trial)
        except IntegrityError as e:
            await db.rollback()
            logger.error(f"Database integrity error updating trial: {e}")
            raise ConflictError("Failed to update trial due to constraint violation")

    @staticmethod
    async def link_system(
        db: AsyncSession,
        trial_id: UUID,
        link_data: SystemLinkCreate,
        user_email: str,
    ) -> SystemLinkResponse:
        """Link a system to a trial."""
        logger.info(
            f"Linking system {link_data.instance_id} to trial {trial_id} by {user_email}"
        )

        # Verify trial exists
        trial_query = select(Trial).where(Trial.trial_id == trial_id)
        trial_result = await db.execute(trial_query)
        if not trial_result.scalar_one_or_none():
            raise NotFoundError("Trial", trial_id)

        # Verify system exists
        system_query = select(SystemInstance).where(
            SystemInstance.instance_id == link_data.instance_id
        )
        system_result = await db.execute(system_query)
        if not system_result.scalar_one_or_none():
            raise NotFoundError("System", link_data.instance_id)

        # Check for existing active link
        existing_link_query = select(TrialSystemLink).where(
            and_(
                TrialSystemLink.trial_id == trial_id,
                TrialSystemLink.instance_id == link_data.instance_id,
                TrialSystemLink.unlinked_at.is_(None),
            )
        )
        existing_result = await db.execute(existing_link_query)
        if existing_result.scalar_one_or_none():
            raise ConflictError(
                f"System {link_data.instance_id} is already linked to trial {trial_id}"
            )

        # Create link
        link = TrialSystemLink(
            trial_id=trial_id,
            instance_id=link_data.instance_id,
            criticality_code=link_data.criticality_code,
            criticality_override_reason=link_data.criticality_override_reason,
            usage_start_date=link_data.usage_start_date or datetime.utcnow().date(),
            usage_end_date=link_data.usage_end_date,
            linked_by=user_email,
        )

        try:
            db.add(link)
            await db.commit()
            await db.refresh(link)
            logger.info(f"System linked: {link.link_id}")
            return SystemLinkResponse.model_validate(link)
        except IntegrityError as e:
            await db.rollback()
            logger.error(f"Database integrity error linking system: {e}")
            raise ConflictError("Failed to link system due to constraint violation")

    @staticmethod
    async def update_system_link(
        db: AsyncSession,
        trial_id: UUID,
        instance_id: UUID,
        link_data: SystemLinkUpdate,
        user_email: str,
    ) -> SystemLinkResponse:
        """Update a trial-system link."""
        logger.info(
            f"Updating link for system {instance_id} in trial {trial_id} by {user_email}"
        )

        # Get link
        link_query = select(TrialSystemLink).where(
            and_(
                TrialSystemLink.trial_id == trial_id,
                TrialSystemLink.instance_id == instance_id,
                TrialSystemLink.unlinked_at.is_(None),
            )
        )
        link_result = await db.execute(link_query)
        link = link_result.scalar_one_or_none()

        if not link:
            raise NotFoundError(
                "Active link",
                f"system {instance_id} in trial {trial_id}"
            )

        # Update fields
        update_data = link_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(link, key, value)

        link.updated_at = datetime.utcnow()

        try:
            await db.commit()
            await db.refresh(link)
            logger.info(f"System link updated: {link.link_id}")
            return SystemLinkResponse.model_validate(link)
        except IntegrityError as e:
            await db.rollback()
            logger.error(f"Database integrity error updating link: {e}")
            raise ConflictError("Failed to update link due to constraint violation")

    @staticmethod
    async def unlink_system(
        db: AsyncSession, trial_id: UUID, instance_id: UUID, user_email: str
    ) -> None:
        """Unlink a system from a trial (soft delete)."""
        logger.info(
            f"Unlinking system {instance_id} from trial {trial_id} by {user_email}"
        )

        # Get link
        link_query = select(TrialSystemLink).where(
            and_(
                TrialSystemLink.trial_id == trial_id,
                TrialSystemLink.instance_id == instance_id,
                TrialSystemLink.unlinked_at.is_(None),
            )
        )
        link_result = await db.execute(link_query)
        link = link_result.scalar_one_or_none()

        if not link:
            raise NotFoundError(
                "Active link",
                f"system {instance_id} in trial {trial_id}"
            )

        # Soft delete
        link.unlinked_by = user_email
        link.unlinked_at = datetime.utcnow()
        link.updated_at = datetime.utcnow()

        await db.commit()
        logger.info(f"System unlinked: {link.link_id}")
