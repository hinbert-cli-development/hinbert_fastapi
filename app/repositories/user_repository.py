"""User-specific query repository."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain.user import User


async def get_by_email(session: AsyncSession, email: str) -> User | None:
    """Find a user by normalized email using a bound SQL expression."""
    return await session.scalar(select(User).where(User.email == email.lower()))
