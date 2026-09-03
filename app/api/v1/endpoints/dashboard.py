"""Operational dashboard endpoint placeholder for aggregated metrics."""

from fastapi import APIRouter

from app.models.schemas.response import APIResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=APIResponse[dict[str, int]])
async def stats():
    """Return a stable metric contract ready for warehouse-backed aggregates."""
    return APIResponse(data={"users": 0, "products": 0})
