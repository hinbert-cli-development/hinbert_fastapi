"""Product creation and query rules."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain.product import Product
from app.models.schemas.product import ProductCreate


async def create_product(session: AsyncSession, payload: ProductCreate) -> Product:
    """Create and return a product after transaction commit."""
    product = Product(**payload.model_dump())
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product
