"""FastAPI dependency that yields and closes one async DB session."""

from collections.abc import AsyncGenerator

from app.core.config.database import SessionLocal


async def get_db() -> AsyncGenerator:
    """Yield a request-scoped SQLAlchemy session and always close it."""
    async with SessionLocal() as session:
        yield session
