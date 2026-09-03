"""Refresh-token persistence and revocation queries."""

from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain.refresh_token import RefreshToken


async def find_active(session: AsyncSession, token_hash: str) -> RefreshToken | None:
    """Find a non-revoked, non-expired hashed token."""
    return await session.scalar(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked_at.is_(None),
            RefreshToken.expires_at > datetime.now(UTC),
        )
    )


async def create(session: AsyncSession, token: RefreshToken) -> RefreshToken:
    """Persist a hashed refresh token and its expiry."""
    session.add(token)
    await session.commit()
    await session.refresh(token)
    return token


async def revoke(session: AsyncSession, token: RefreshToken) -> None:
    """Revoke a refresh token without deleting its audit record."""
    token.revoked_at = datetime.now(UTC)
    await session.commit()


async def delete_expired(session: AsyncSession) -> int:
    """Delete expired refresh tokens and return the affected row count."""
    result = await session.execute(delete(RefreshToken).where(RefreshToken.expires_at <= datetime.now(UTC)))
    await session.commit()
    return result.rowcount or 0
