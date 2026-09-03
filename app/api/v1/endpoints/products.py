"""Paginated product CRUD endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_active_user
from app.api.deps.pagination import pagination
from app.db.session import get_db
from app.models.domain.product import Product
from app.models.domain.user import User
from app.models.schemas.product import ProductCreate, ProductOut
from app.models.schemas.response import APIResponse
from app.repositories.base.base_repository import BaseRepository
from app.services.product_service import create_product

router = APIRouter(prefix="/products", tags=["products"])


@router.post("", response_model=APIResponse[ProductOut], status_code=201)
async def create(
    payload: ProductCreate, _: User = Depends(get_current_active_user), session: AsyncSession = Depends(get_db)
):
    """Create a product for an authenticated account."""
    return APIResponse(message="Product created", data=await create_product(session, payload), status_code=201)


@router.get("", response_model=APIResponse[list[ProductOut]])
async def list_products(page: tuple[int, int] = Depends(pagination), session: AsyncSession = Depends(get_db)):
    """Return a bounded product page."""
    items = await BaseRepository(session, Product).list(*page)
    return APIResponse(data=items)
