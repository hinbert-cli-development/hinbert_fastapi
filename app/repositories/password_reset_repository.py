"""Password-reset token persistence and single-use lookup operations."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain.password_reset import PasswordReset


async def create(session: AsyncSession, token: PasswordReset) -> PasswordReset:
    """Persist a hashed, expiring reset token."""
    session.add(token)
    await session.commit()
    await session.refresh(token)
    return token


async def get_by_token(session: AsyncSession, token_hash: str) -> PasswordReset | None:
    """Find an unused and unexpired reset token by digest."""
    return await session.scalar(
        select(PasswordReset).where(
            PasswordReset.token_hash == token_hash,
            PasswordReset.used_at.is_(None),
            PasswordReset.expires_at > datetime.now(UTC),
        )
    )


async def mark_used(session: AsyncSession, token: PasswordReset) -> None:
    """Mark a reset token unusable after a successful password change."""
    token.used_at = datetime.now(UTC)
    await session.commit()
