"""Integration tests for profile and administrator user management."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.password import hash_password
from app.models.domain.user import User


async def login(client: AsyncClient, email: str, password: str) -> str:
    """Return an access token from the credential login endpoint."""
    response = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return response.json()["data"]["access_token"]


@pytest.mark.asyncio
async def test_current_user_can_update_profile(client: AsyncClient):
    """Authenticated users can update their own display name."""
    await client.post(
        "/api/v1/auth/signup",
        json={"email": "profile@example.com", "full_name": "Original", "password": "StrongPassword!123"},
    )
    token = await login(client, "profile@example.com", "StrongPassword!123")
    response = await client.patch(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}, json={"full_name": "Updated"}
    )
    assert response.status_code == 200
    assert response.json()["data"]["full_name"] == "Updated"


@pytest.mark.asyncio
async def test_non_admin_cannot_list_users(client: AsyncClient):
    """Regular accounts cannot access administrator user listings."""
    await client.post(
        "/api/v1/auth/signup",
        json={"email": "member@example.com", "full_name": "Member", "password": "StrongPassword!123"},
    )
    token = await login(client, "member@example.com", "StrongPassword!123")
    response = await client.get("/api/v1/users", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_admin_can_list_and_update_users(client: AsyncClient, database_session: AsyncSession):
    """Administrators can list users and change a user's active state."""
    admin = User(
        email="admin@example.com",
        full_name="Admin",
        password_hash=hash_password("AdminPassword!123"),
        is_admin=True,
        is_verified=True,
    )
    database_session.add(admin)
    await database_session.commit()
    await client.post(
        "/api/v1/auth/signup",
        json={"email": "managed@example.com", "full_name": "Managed", "password": "StrongPassword!123"},
    )
    token = await login(client, "admin@example.com", "AdminPassword!123")
    listing = await client.get("/api/v1/users", headers={"Authorization": f"Bearer {token}"})
    assert listing.status_code == 200
    managed = next(item for item in listing.json()["data"] if item["email"] == "managed@example.com")
    updated = await client.patch(
        f"/api/v1/users/{managed['id']}", headers={"Authorization": f"Bearer {token}"}, json={"is_active": False}
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["is_active"] is False
