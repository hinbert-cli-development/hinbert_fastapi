"""Product CRUD endpoints with bounded filtering, sorting, and pagination."""

from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_active_user
from app.api.deps.pagination import pagination
from app.core.exceptions.custom_exceptions import NotFoundError, UnauthorizedError
from app.core.middleware.rate_limit import limiter
from app.db.session import get_db
from app.models.domain.product import Product
from app.models.domain.user import User
from app.models.schemas.product import ProductCreate, ProductOut, ProductPage
from app.models.schemas.response import APIResponse
from app.repositories.product_repository import ProductRepository
from app.services.product_service import create_product, update_product

router = APIRouter(prefix="/products", tags=["products"])


@router.post("", response_model=APIResponse[ProductOut], status_code=201)
@limiter.limit("60/minute")
async def create(
    request: Request,
    payload: ProductCreate,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
):
    """Create a product owned by the authenticated user."""
    product = await create_product(session, payload)
    product.owner_id = user.id
    await session.commit()
    return APIResponse(message="Product created", data=product, status_code=201)


@router.get("", response_model=APIResponse[ProductPage])
@limiter.limit("120/minute")
async def list_products(
    request: Request,
    page: tuple[int, int] = Depends(pagination),
    category: str | None = None,
    min_price: Decimal | None = Query(None, ge=0),
    max_price: Decimal | None = Query(None, ge=0),
    sort_by: str = Query("created_at", pattern="^(name|price|created_at)$"),
    session: AsyncSession = Depends(get_db),
):
    """Return products and deterministic pagination metadata."""
    offset, limit = page
    items = await ProductRepository(session).get_all(offset, limit, category, min_price, max_price, sort_by)
    total = await session.scalar(select(func.count()).select_from(Product))
    return APIResponse(data={"items": items, "total_count": total or 0, "page": offset // limit + 1, "limit": limit})


@router.get("/{product_id}", response_model=APIResponse[ProductOut])
@limiter.limit("120/minute")
async def get_product(request: Request, product_id: UUID, session: AsyncSession = Depends(get_db)):
    """Return one product by UUID."""
    product = await session.get(Product, product_id)
    if product is None:
        raise NotFoundError("Product not found")
    return APIResponse(data=product)


@router.put("/{product_id}", response_model=APIResponse[ProductOut])
@limiter.limit("60/minute")
async def update_product_endpoint(
    request: Request,
    product_id: UUID,
    payload: ProductCreate,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
):
    """Update a product when the caller owns it or is an administrator."""
    product = await session.get(Product, product_id)
    if product is None:
        raise NotFoundError("Product not found")
    if product.owner_id not in {None, user.id} and not user.is_admin:
        raise UnauthorizedError("Product ownership required")
    return APIResponse(data=await update_product(session, product, payload), message="Product updated")


@router.delete("/{product_id}", response_model=APIResponse[None])
@limiter.limit("60/minute")
async def delete_product(
    request: Request,
    product_id: UUID,
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
):
    """Delete a product when the caller owns it or is an administrator."""
    product = await session.get(Product, product_id)
    if product is None:
        raise NotFoundError("Product not found")
    if product.owner_id not in {None, user.id} and not user.is_admin:
        raise UnauthorizedError("Product ownership required")
    await session.delete(product)
    await session.commit()
    return APIResponse(message="Product deleted", data=None)
