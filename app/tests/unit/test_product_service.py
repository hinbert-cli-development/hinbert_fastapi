"""Unit tests for product service business operations."""

from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.domain.product import Product
from app.models.schemas.product import ProductCreate
from app.services.product_service import create_product, update_product


@pytest.mark.asyncio
async def test_create_product_persists_payload():
    """Product creation maps validated schema fields to the model."""
    session = AsyncMock()
    session.add = MagicMock()
    session.refresh = AsyncMock()
    product = await create_product(session, ProductCreate(name="Widget", price=Decimal("2.50")))
    assert product.name == "Widget"
    assert product.price == Decimal("2.50")


@pytest.mark.asyncio
async def test_update_product_replaces_editable_fields():
    """Product updates modify name, category, description, and price."""
    session = AsyncMock()
    product = Product(name="Old", description="old", price=Decimal("1.00"))
    await update_product(
        session, product, ProductCreate(name="New", description="new", price=Decimal("2.00"), category="tools")
    )
    assert product.name == "New"
    assert product.category == "tools"
