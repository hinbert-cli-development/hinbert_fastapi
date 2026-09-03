"""Validated pagination dependency shared by collection endpoints."""

from fastapi import Query


def pagination(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)) -> tuple[int, int]:
    """Return SQL offset and bounded page size."""
    return (page - 1) * page_size, page_size
