"""Encrypted TOTP-secret persistence operations."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain.totp_secret import TotpSecret


async def get(session: AsyncSession, user_id) -> TotpSecret | None:
    """Load the encrypted secret belonging to a user."""
    return await session.get(TotpSecret, user_id)


async def create_or_replace(session: AsyncSession, secret: TotpSecret) -> TotpSecret:
    """Insert or replace a user's encrypted TOTP secret."""
    existing = await session.get(TotpSecret, secret.user_id)
    if existing is not None:
        existing.secret = secret.secret
        secret = existing
    else:
        session.add(secret)
    await session.commit()
    await session.refresh(secret)
    return secret
