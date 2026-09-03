"""Product-specific query repository."""

from app.models.domain.product import Product
from app.repositories.base.base_repository import BaseRepository


class ProductRepository(BaseRepository[Product]):
    """Repository configured for product queries."""

    def __init__(self, session):
        super().__init__(session, Product)
