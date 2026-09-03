"""User business rules and safe profile operations."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.password import hash_password
from app.models.domain.user import User
from app.models.schemas.user import UserCreate, UserUpdate


async def create_user(session: AsyncSession, payload: UserCreate) -> User:
    """Create a user with a bcrypt hash and commit the transaction."""
    user = User(
        email=str(payload.email).lower(), full_name=payload.full_name, password_hash=hash_password(payload.password)
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update_user(session: AsyncSession, user: User, payload: UserUpdate) -> User:
    """Apply allowed profile fields and persist them."""
    if payload.full_name is not None:
        user.full_name = payload.full_name
    await session.commit()
    await session.refresh(user)
    return user
