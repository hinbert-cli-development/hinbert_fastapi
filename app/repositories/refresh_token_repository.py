"""Refresh-token persistence and revocation queries."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain.refresh_token import RefreshToken


async def find_active(session: AsyncSession, token_hash: str) -> RefreshToken | None:
    """Find a non-revoked, non-expired hashed token."""
    return await session.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash, RefreshToken.revoked_at.is_(None))
    )
