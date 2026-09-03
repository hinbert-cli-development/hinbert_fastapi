"""Shared pytest fixtures; replace the database URL with a disposable test DB."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    """Yield an async HTTP client without starting a network server."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
        yield test_client
