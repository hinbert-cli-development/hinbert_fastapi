"""Product CRUD schemas."""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    """Validated product creation payload."""

    name: str = Field(min_length=1, max_length=200)
    description: str = ""
    price: Decimal = Field(ge=0, decimal_places=2)
    category: str = Field(default="general", max_length=100)


class ProductOut(ProductCreate):
    """Product response including database identity."""

    model_config = ConfigDict(from_attributes=True)
    id: UUID
