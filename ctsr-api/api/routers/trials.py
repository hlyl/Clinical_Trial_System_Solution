"""API router for trial management."""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth import User, UserRole, get_current_user, require_role
from api.db.database import get_db
from api.models.trials import (
    TrialCreate,
    TrialUpdate,
    TrialResponse,
    TrialDetail,
    TrialListResponse,
    SystemLinkCreate,
    SystemLinkUpdate,
    SystemLinkResponse,
)
from api.services.trials import TrialService
from api.utils.pagination import PaginationParams

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/trials", tags=["trials"])


@router.get("", response_model=TrialListResponse, status_code=status.HTTP_200_OK)
async def list_trials(
    search: Optional[str] = Query(None, description="Search in protocol number, title, or therapeutic area"),
    trial_status: Optional[str] = Query(None, description="Filter by trial status"),
    trial_phase: Optional[str] = Query(None, description="Filter by trial phase"),
    therapeutic_area: Optional[str] = Query(None, description="Filter by therapeutic area"),
    trial_lead_email: Optional[str] = Query(None, description="Filter by trial lead email"),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.VIEWER)),
):
    """
    List all trials with optional search and filters.
    
    **Permissions:** VIEWER, TRIAL_LEAD, ADMIN
    """
    trials, meta = await TrialService.list_trials(
        db=db,
        pagination=pagination,
        search=search,
        trial_status=trial_status,
        trial_phase=trial_phase,
        therapeutic_area=therapeutic_area,
        trial_lead_email=trial_lead_email,
        user_email=user.email,
    )

    return TrialListResponse(
        data=[TrialResponse.model_validate(trial) for trial in trials],
        meta=meta.model_dump(),
    )


@router.post("", response_model=TrialResponse, status_code=status.HTTP_201_CREATED)
async def create_trial(
    trial_data: TrialCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.TRIAL_LEAD)),
):
    """
    Create a new trial.
    
    **Permissions:** TRIAL_LEAD, ADMIN
    """
    return await TrialService.create_trial(
        db=db, trial_data=trial_data, user_email=user.email
    )


@router.get("/{trial_id}", response_model=TrialDetail, status_code=status.HTTP_200_OK)
async def get_trial(
    trial_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.VIEWER)),
):
    """
    Get trial details including linked systems.
    
    **Permissions:** VIEWER, TRIAL_LEAD, ADMIN
    """
    return await TrialService.get_trial(db=db, trial_id=trial_id, user_email=user.email)


@router.put("/{trial_id}", response_model=TrialResponse, status_code=status.HTTP_200_OK)
async def update_trial(
    trial_id: UUID,
    trial_data: TrialUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.TRIAL_LEAD)),
):
    """
    Update a trial.
    
    **Permissions:** TRIAL_LEAD, ADMIN
    """
    return await TrialService.update_trial(
        db=db, trial_id=trial_id, trial_data=trial_data, user_email=user.email
    )


@router.post(
    "/{trial_id}/systems",
    response_model=SystemLinkResponse,
    status_code=status.HTTP_201_CREATED,
)
async def link_system_to_trial(
    trial_id: UUID,
    link_data: SystemLinkCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.TRIAL_LEAD)),
):
    """
    Link a system to a trial with criticality assignment.
    
    **Permissions:** TRIAL_LEAD, ADMIN
    """
    return await TrialService.link_system(
        db=db, trial_id=trial_id, link_data=link_data, user_email=user.email
    )


@router.put(
    "/{trial_id}/systems/{instance_id}",
    response_model=SystemLinkResponse,
    status_code=status.HTTP_200_OK,
)
async def update_system_link(
    trial_id: UUID,
    instance_id: UUID,
    link_data: SystemLinkUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.TRIAL_LEAD)),
):
    """
    Update a trial-system link (e.g., change criticality).
    
    **Permissions:** TRIAL_LEAD, ADMIN
    """
    return await TrialService.update_system_link(
        db=db,
        trial_id=trial_id,
        instance_id=instance_id,
        link_data=link_data,
        user_email=user.email,
    )


@router.delete(
    "/{trial_id}/systems/{instance_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def unlink_system_from_trial(
    trial_id: UUID,
    instance_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.TRIAL_LEAD)),
):
    """
    Unlink a system from a trial (soft delete).
    
    **Permissions:** TRIAL_LEAD, ADMIN
    """
    await TrialService.unlink_system(
        db=db, trial_id=trial_id, instance_id=instance_id, user_email=user.email
    )
    return None
