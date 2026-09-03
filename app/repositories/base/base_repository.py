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

    async def get_by_id(self, item_id: UUID) -> ModelT | None:
        """Alias with an explicit name for service and endpoint callers."""
        return await self.get(item_id)

    async def create(self, instance: ModelT) -> ModelT:
        """Persist, commit, and refresh a new model instance."""
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def update(self, instance: ModelT, values: dict[str, object]) -> ModelT:
        """Apply a whitelist prepared by the caller and persist the model."""
        for field, value in values.items():
            setattr(instance, field, value)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def delete(self, instance: ModelT) -> None:
        """Delete an instance and commit the transaction."""
        await self.session.delete(instance)
        await self.session.commit()

    async def list(self, offset: int = 0, limit: int = 50) -> list[ModelT]:
        """Return a bounded page, preventing unbounded database reads."""
        result = await self.session.scalars(select(self.model).offset(offset).limit(min(limit, 100)))
        return list(result)
