"""Operational dashboard endpoint placeholder for aggregated metrics."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import get_current_admin
from app.core.middleware.rate_limit import limiter
from app.db.session import get_db
from app.models.domain.product import Product
from app.models.domain.user import User
from app.models.schemas.response import APIResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=APIResponse[dict[str, int]])
@limiter.limit("60/minute")
async def stats(request: Request, _: User = Depends(get_current_admin), session: AsyncSession = Depends(get_db)):
    """Return current user and product counts for administrators."""
    users = await session.scalar(select(func.count()).select_from(User))
    products = await session.scalar(select(func.count()).select_from(Product))
    return APIResponse(data={"users": users or 0, "products": products or 0, "active_sessions": 0})
