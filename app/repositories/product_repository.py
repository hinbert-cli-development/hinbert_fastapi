"""Product-specific query repository."""

from decimal import Decimal

from sqlalchemy import select

from app.models.domain.product import Product
from app.repositories.base.base_repository import BaseRepository


class ProductRepository(BaseRepository[Product]):
    """Repository configured for product queries."""

    def __init__(self, session):
        super().__init__(session, Product)

    async def get_all(
        self,
        offset: int = 0,
        limit: int = 50,
        category: str | None = None,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        sort_by: str = "created_at",
    ) -> list[Product]:
        """Return a bounded, filtered, allowlisted-sorted product page."""
        columns = {"name": Product.name, "price": Product.price, "created_at": Product.created_at}
        query = select(Product)
        if category:
            query = query.where(Product.category == category)
        if min_price is not None:
            query = query.where(Product.price >= min_price)
        if max_price is not None:
            query = query.where(Product.price <= max_price)
        query = query.order_by(columns.get(sort_by, Product.created_at)).offset(offset).limit(min(limit, 100))
        return list(await self.session.scalars(query))

    async def get_by_id(self, product_id):
        """Return a product by UUID."""
        return await self.get(product_id)
