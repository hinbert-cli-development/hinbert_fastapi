"""Generic service helpers that keep endpoint code thin."""

from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseService(Generic[ModelT]):
    """Provide common async lookup behavior for a model service."""

    def __init__(self, model: type[ModelT], session: AsyncSession):
        self.model, self.session = model, session

    async def get(self, item_id: UUID) -> ModelT | None:
        """Fetch one row by primary key, returning None when absent."""
        return await self.session.get(self.model, item_id)
