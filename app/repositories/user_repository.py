"""User-specific query repository."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain.user import User


async def get_by_email(session: AsyncSession, email: str) -> User | None:
    """Find a user by normalized email using a bound SQL expression."""
    return await session.scalar(select(User).where(User.email == email.lower()))


async def get_by_id(session: AsyncSession, user_id) -> User | None:
    """Return a user by UUID."""
    return await session.get(User, user_id)


async def get_all(session: AsyncSession, offset: int = 0, limit: int = 50) -> list[User]:
    """Return a bounded user page."""
    return list(await session.scalars(select(User).offset(offset).limit(min(limit, 100))))


async def create(session: AsyncSession, user: User) -> User:
    """Persist a user and refresh generated fields."""
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update(session: AsyncSession, user: User, values: dict[str, object]) -> User:
    """Update approved user fields and commit."""
    for field, value in values.items():
        setattr(user, field, value)
    await session.commit()
    await session.refresh(user)
    return user


async def delete(session: AsyncSession, user: User) -> None:
    """Delete a user and dependent owned records."""
    await session.delete(user)
    await session.commit()
