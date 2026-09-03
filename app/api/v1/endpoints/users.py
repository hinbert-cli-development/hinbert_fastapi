"""Authenticated profile and administrator user-management endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_active_user, get_current_admin
from app.api.deps.pagination import pagination
from app.core.middleware.rate_limit import limiter
from app.db.session import get_db
from app.models.domain.user import User
from app.models.schemas.response import APIResponse
from app.models.schemas.user import AdminUserUpdate, UserOut, UserUpdate
from app.repositories import user_repository
from app.services.user_service import update_user

router = APIRouter(prefix="/users", tags=["users"])


@router.patch("/me", response_model=APIResponse[UserOut])
@limiter.limit("60/minute")
async def update_me(
    request: Request,
    payload: UserUpdate,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
):
    """Update allowed profile fields for the current account."""
    return APIResponse(data=await update_user(session, user, payload), message="Profile updated")


@router.get("", response_model=APIResponse[list[UserOut]])
@limiter.limit("60/minute")
async def list_users(
    request: Request,
    page: tuple[int, int] = Depends(pagination),
    _: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db),
):
    """List users for administrators with bounded pagination."""
    return APIResponse(data=await user_repository.get_all(session, *page))


@router.get("/{user_id}", response_model=APIResponse[UserOut])
@limiter.limit("60/minute")
async def get_user(
    request: Request, user_id: UUID, _: User = Depends(get_current_admin), session: AsyncSession = Depends(get_db)
):
    """Return one user to an administrator."""
    user = await user_repository.get_by_id(session, user_id)
    if user is None:
        from app.core.exceptions.custom_exceptions import NotFoundError

        raise NotFoundError("User not found")
    return APIResponse(data=user)


@router.patch("/{user_id}", response_model=APIResponse[UserOut])
@limiter.limit("30/minute")
async def update_user_admin(
    request: Request,
    user_id: UUID,
    payload: AdminUserUpdate,
    _: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db),
):
    """Update profile and role fields as an administrator."""
    user = await user_repository.get_by_id(session, user_id)
    if user is None:
        from app.core.exceptions.custom_exceptions import NotFoundError

        raise NotFoundError("User not found")
    return APIResponse(data=await user_repository.update(session, user, payload.model_dump(exclude_none=True)))


@router.delete("/{user_id}", response_model=APIResponse[None])
@limiter.limit("30/minute")
async def delete_user(
    request: Request, user_id: UUID, _: User = Depends(get_current_admin), session: AsyncSession = Depends(get_db)
):
    """Hard-delete a user and dependent records as an administrator."""
    user = await user_repository.get_by_id(session, user_id)
    if user is None:
        from app.core.exceptions.custom_exceptions import NotFoundError

        raise NotFoundError("User not found")
    await user_repository.delete(session, user)
    return APIResponse(message="User deleted", data=None)
