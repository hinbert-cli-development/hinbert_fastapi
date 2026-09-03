"""Declarative SQLAlchemy base imported by Alembic and model modules."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Common parent for all database tables."""
