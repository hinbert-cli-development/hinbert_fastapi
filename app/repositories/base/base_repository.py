"""Generic async CRUD repository using SQLAlchemy expressions."""

from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Provide safe parameterized lookup and paginated listing primitives."""

    def __init__(self, session: AsyncSession, model: type[ModelT]):
        self.session, self.model = session, model

    async def get(self, item_id: UUID) -> ModelT | None:
        """Fetch by primary key using SQLAlchemy's bound parameters."""
        return await self.session.get(self.model, item_id)

    async def list(self, offset: int = 0, limit: int = 50) -> list[ModelT]:
        """Return a bounded page, preventing unbounded database reads."""
        result = await self.session.scalars(select(self.model).offset(offset).limit(min(limit, 100)))
        return list(result)
