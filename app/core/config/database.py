"""Async SQLAlchemy engine and session factory.

The engine is created lazily at import time and sessions are request-scoped by
dependency. Pool values should be tuned to deployment capacity, not guessed in
individual endpoints.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config.settings import get_settings

engine = create_async_engine(get_settings().database_url, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
