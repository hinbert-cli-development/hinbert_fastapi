"""Email verification token query boundary."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain.email_verification import EmailVerification


async def save(session: AsyncSession, token: EmailVerification) -> EmailVerification:
    """Persist a pre-hashed verification token."""
    session.add(token)
    await session.commit()
    return token


async def create(session: AsyncSession, token: EmailVerification) -> EmailVerification:
    """Persist a verification token using the repository naming convention."""
    return await save(session, token)


async def get_by_token(session: AsyncSession, token_hash: str) -> EmailVerification | None:
    """Find an unused and unexpired verification token by digest."""
    return await session.scalar(
        select(EmailVerification).where(
            EmailVerification.token_hash == token_hash,
            EmailVerification.used_at.is_(None),
            EmailVerification.expires_at > datetime.now(UTC),
        )
    )


async def mark_used(session: AsyncSession, token: EmailVerification) -> None:
    """Mark a verification token as consumed."""
    token.used_at = datetime.now(UTC)
    await session.commit()
