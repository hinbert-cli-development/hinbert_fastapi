"""Authenticated user profile endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_active_user
from app.db.session import get_db
from app.models.domain.user import User
from app.models.schemas.response import APIResponse
from app.models.schemas.user import UserOut, UserUpdate
from app.services.user_service import update_user

router = APIRouter(prefix="/users", tags=["users"])


@router.patch("/me", response_model=APIResponse[UserOut])
async def update_me(
    payload: UserUpdate, user: User = Depends(get_current_active_user), session: AsyncSession = Depends(get_db)
):
    """Update allowed profile fields for the current account."""
    return APIResponse(data=await update_user(session, user, payload), message="Profile updated")
