"""Integration tests for credential, token, and TOTP authentication flows."""

import pyotp
import pytest
from httpx import AsyncClient

from app.api.v1.endpoints import auth as auth_endpoint


@pytest.mark.asyncio
async def test_signup_and_login(client: AsyncClient):
    """Signup returns a safe user and login returns both token types."""
    signup = await client.post(
        "/api/v1/auth/signup",
        json={"email": "user@example.com", "full_name": "Test User", "password": "StrongPassword!123"},
    )
    assert signup.status_code == 201
    assert "password_hash" not in signup.text
    login = await client.post(
        "/api/v1/auth/login", json={"email": "user@example.com", "password": "StrongPassword!123"}
    )
    assert login.status_code == 200
    assert login.json()["data"]["access_token"]
    assert login.json()["data"]["refresh_token"]


@pytest.mark.asyncio
async def test_refresh_rotation_and_logout(client: AsyncClient):
    """A refresh token rotates once and logout revokes its replacement."""
    await client.post(
        "/api/v1/auth/signup",
        json={"email": "rotate@example.com", "full_name": "Rotate User", "password": "StrongPassword!123"},
    )
    login = await client.post(
        "/api/v1/auth/login", json={"email": "rotate@example.com", "password": "StrongPassword!123"}
    )
    first_refresh = login.json()["data"]["refresh_token"]
    refreshed = await client.post("/api/v1/auth/refresh", json={"refresh_token": first_refresh})
    assert refreshed.status_code == 200
    second_refresh = refreshed.json()["data"]["refresh_token"]
    assert second_refresh != first_refresh
    assert (await client.post("/api/v1/auth/refresh", json={"refresh_token": first_refresh})).status_code == 401
    assert (await client.post("/api/v1/auth/logout", json={"refresh_token": second_refresh})).status_code == 200
    assert (await client.post("/api/v1/auth/refresh", json={"refresh_token": second_refresh})).status_code == 401


@pytest.mark.asyncio
async def test_invalid_login_returns_401(client: AsyncClient):
    """Invalid credentials are rejected without account detail leakage."""
    response = await client.post(
        "/api/v1/auth/login", json={"email": "missing@example.com", "password": "WrongPassword!123"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_totp_setup_and_verify(client: AsyncClient):
    """TOTP setup returns a provisioning URI and accepts a current code."""
    await client.post(
        "/api/v1/auth/signup",
        json={"email": "totp@example.com", "full_name": "TOTP User", "password": "StrongPassword!123"},
    )
    login = await client.post(
        "/api/v1/auth/login", json={"email": "totp@example.com", "password": "StrongPassword!123"}
    )
    headers = {"Authorization": f"Bearer {login.json()['data']['access_token']}"}
    setup = await client.post("/api/v1/auth/totp/setup", headers=headers)
    assert setup.status_code == 200
    secret = setup.json()["data"]["secret"]
    verify = await client.post("/api/v1/auth/totp/verify", headers=headers, json={"code": pyotp.TOTP(secret).now()})
    assert verify.status_code == 200


@pytest.mark.asyncio
async def test_email_verification_activates_account(client: AsyncClient, monkeypatch):
    """Signup creates a token that activates the account when consumed."""
    sent = {}
    monkeypatch.setattr(auth_endpoint, "send_verification_email", lambda user, token: sent.setdefault("token", token))
    response = await client.post(
        "/api/v1/auth/signup",
        json={"email": "verify@example.com", "full_name": "Verify", "password": "StrongPassword!123"},
    )
    assert response.status_code == 201
    verified = await client.post("/api/v1/auth/verify-email", json={"token": sent["token"]})
    assert verified.status_code == 200


@pytest.mark.asyncio
async def test_forgot_and_reset_password(client: AsyncClient, monkeypatch):
    """Forgot-password creates a reset token that changes the login credential."""
    sent = {}
    monkeypatch.setattr(auth_endpoint, "send_reset_email", lambda user, token: sent.setdefault("token", token))
    await client.post(
        "/api/v1/auth/signup",
        json={"email": "reset@example.com", "full_name": "Reset", "password": "StrongPassword!123"},
    )
    forgotten = await client.post("/api/v1/auth/forgot-password", json={"email": "reset@example.com"})
    assert forgotten.status_code == 200
    reset = await client.post(
        "/api/v1/auth/reset-password", json={"token": sent["token"], "password": "NewStrongPassword!123"}
    )
    assert reset.status_code == 200
    assert (
        await client.post(
            "/api/v1/auth/login", json={"email": "reset@example.com", "password": "NewStrongPassword!123"}
        )
    ).status_code == 200


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    """The liveness endpoint is available without database access."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
