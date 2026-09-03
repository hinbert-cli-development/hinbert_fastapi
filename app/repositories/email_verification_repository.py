"""Email verification token query boundary."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain.email_verification import EmailVerification


async def save(session: AsyncSession, token: EmailVerification) -> EmailVerification:
    """Persist a pre-hashed verification token."""
    session.add(token)
    await session.commit()
    return token
