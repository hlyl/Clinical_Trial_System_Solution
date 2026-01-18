"""API router for confirmation management."""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth import User, UserRole, get_current_user, require_role
from api.db.database import get_db
from api.models.confirmations import (
    ConfirmationCreate,
    ConfirmationDetail,
    ConfirmationListResponse,
    ConfirmationResponse,
    ConfirmationSubmit,
    ConfirmationUpdate,
    ExportRequest,
    ExportResponse,
)
from api.services.confirmations import ConfirmationService
from api.utils.pagination import PaginationParams

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/confirmations", tags=["confirmations"])


@router.get("", response_model=ConfirmationListResponse, status_code=status.HTTP_200_OK)
async def list_confirmations(
    trial_id: Optional[UUID] = Query(None, description="Filter by trial ID"),
    confirmation_status: Optional[str] = Query(None, description="Filter by status (PENDING/COMPLETED/OVERDUE)"),
    confirmation_type: Optional[str] = Query(None, description="Filter by type (PERIODIC/DB_LOCK)"),
    overdue_only: bool = Query(False, description="Show only overdue confirmations"),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.VIEWER)),
):
    """
    List all confirmations with optional filters.

    **Permissions:** VIEWER, TRIAL_LEAD, ADMIN
    """
    confirmations, meta = await ConfirmationService.list_confirmations(
        db=db,
        pagination=pagination,
        trial_id=trial_id,
        confirmation_status=confirmation_status,
        confirmation_type=confirmation_type,
        overdue_only=overdue_only,
        user_email=user.email,
    )

    return ConfirmationListResponse(
        data=[ConfirmationResponse.model_validate(conf) for conf in confirmations],
        meta=meta.model_dump(),
    )


@router.post("", response_model=ConfirmationResponse, status_code=status.HTTP_201_CREATED)
async def create_confirmation(
    confirmation_data: ConfirmationCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.TRIAL_LEAD)),
):
    """
    Create a new confirmation for a trial.

    **Permissions:** TRIAL_LEAD, ADMIN
    """
    return await ConfirmationService.create_confirmation(
        db=db, confirmation_data=confirmation_data, user_email=user.email
    )


@router.get("/{confirmation_id}", response_model=ConfirmationDetail, status_code=status.HTTP_200_OK)
async def get_confirmation(
    confirmation_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.VIEWER)),
):
    """
    Get confirmation details including system snapshots.

    **Permissions:** VIEWER, TRIAL_LEAD, ADMIN
    """
    return await ConfirmationService.get_confirmation(db=db, confirmation_id=confirmation_id, user_email=user.email)


@router.put("/{confirmation_id}", response_model=ConfirmationResponse, status_code=status.HTTP_200_OK)
async def update_confirmation(
    confirmation_id: UUID,
    confirmation_data: ConfirmationUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.TRIAL_LEAD)),
):
    """
    Update a confirmation (only pending confirmations can be updated).

    **Permissions:** TRIAL_LEAD, ADMIN
    """
    return await ConfirmationService.update_confirmation(
        db=db,
        confirmation_id=confirmation_id,
        confirmation_data=confirmation_data,
        user_email=user.email,
    )


@router.post(
    "/{confirmation_id}/submit",
    response_model=ConfirmationResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_confirmation(
    confirmation_id: UUID,
    submit_data: ConfirmationSubmit,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.TRIAL_LEAD)),
):
    """
    Submit a confirmation and optionally capture system snapshots.

    **Permissions:** TRIAL_LEAD, ADMIN
    """
    return await ConfirmationService.submit_confirmation(
        db=db,
        confirmation_id=confirmation_id,
        submit_data=submit_data,
        user_email=user.email,
    )


@router.post("/exports", response_model=ExportResponse, status_code=status.HTTP_201_CREATED)
async def generate_export(
    export_request: ExportRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.TRIAL_LEAD)),
):
    """
    Generate an eTMF export for a completed confirmation.

    **Permissions:** TRIAL_LEAD, ADMIN
    """
    return await ConfirmationService.generate_export(db=db, export_request=export_request, user_email=user.email)
