"""Integration tests for product CRUD, ownership, and query controls."""

import pytest
from httpx import AsyncClient


async def product_token(client: AsyncClient) -> str:
    """Create a test user and return its access token."""
    await client.post(
        "/api/v1/auth/signup",
        json={"email": "products@example.com", "full_name": "Products", "password": "StrongPassword!123"},
    )
    response = await client.post(
        "/api/v1/auth/login", json={"email": "products@example.com", "password": "StrongPassword!123"}
    )
    return response.json()["data"]["access_token"]


@pytest.mark.asyncio
async def test_product_crud(client: AsyncClient):
    """An owner can create, read, update, and delete a product."""
    token = await product_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    created = await client.post(
        "/api/v1/products",
        headers=headers,
        json={"name": "Widget", "description": "A widget", "price": "12.50", "category": "tools"},
    )
    assert created.status_code == 201
    product_id = created.json()["data"]["id"]
    assert (await client.get(f"/api/v1/products/{product_id}")).status_code == 200
    updated = await client.put(
        f"/api/v1/products/{product_id}",
        headers=headers,
        json={"name": "Better Widget", "description": "Updated", "price": "15.00", "category": "tools"},
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["name"] == "Better Widget"
    assert (await client.delete(f"/api/v1/products/{product_id}", headers=headers)).status_code == 200
    assert (await client.get(f"/api/v1/products/{product_id}")).status_code == 404


@pytest.mark.asyncio
async def test_product_filter_sort_and_pagination(client: AsyncClient):
    """The collection endpoint applies category, price, sort, and page controls."""
    token = await product_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    for name, price in (("Cheap", "5.00"), ("Expensive", "50.00")):
        response = await client.post(
            "/api/v1/products", headers=headers, json={"name": name, "price": price, "category": "tools"}
        )
        assert response.status_code == 201
    response = await client.get("/api/v1/products?page=1&page_size=1&category=tools&min_price=10&sort_by=price")
    data = response.json()["data"]
    assert data["total_count"] == 2
    assert data["page"] == 1
    assert data["limit"] == 1
    assert data["items"][0]["name"] == "Expensive"
