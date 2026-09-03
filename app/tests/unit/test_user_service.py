"""Unit tests for user service business operations."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.domain.user import User
from app.models.schemas.user import UserCreate, UserUpdate
from app.services.user_service import create_user, update_user


@pytest.mark.asyncio
async def test_create_user_hashes_password():
    """User creation persists a bcrypt hash rather than plaintext."""
    session = AsyncMock()
    session.add = MagicMock()
    session.refresh = AsyncMock()
    user = await create_user(
        session, UserCreate(email="new@example.com", full_name="New", password="StrongPassword!123")
    )
    assert user.password_hash != "StrongPassword!123"
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_user_changes_only_allowed_profile_field():
    """Profile updates do not alter role or credential fields."""
    session = AsyncMock()
    user = User(email="user@example.com", full_name="Before", password_hash="hash", is_admin=False)
    await update_user(session, user, UserUpdate(full_name="After"))
    assert user.full_name == "After"
    assert user.is_admin is False
