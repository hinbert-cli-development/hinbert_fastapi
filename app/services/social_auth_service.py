"""Social-login provider adapters for Google and Facebook."""

import httpx

from app.core.config.settings import get_settings


async def exchange_provider_code(provider: str, code: str) -> dict[str, str]:
    """Exchange an authorization code for normalized provider user information."""
    if provider not in {"google", "facebook"}:
        raise ValueError("Unsupported provider")
    settings = get_settings()
    async with httpx.AsyncClient(timeout=10) as client:
        if provider == "google":
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret.get_secret_value(),
                    "grant_type": "authorization_code",
                },
            )
            token_response.raise_for_status()
            profile = await client.get(
                "https://openidconnect.googleapis.com/v1/userinfo",
                headers={"Authorization": f"Bearer {token_response.json()['access_token']}"},
            )
        else:
            token_response = await client.get(
                "https://graph.facebook.com/v19.0/oauth/access_token",
                params={
                    "client_id": settings.facebook_client_id,
                    "client_secret": settings.facebook_client_secret.get_secret_value(),
                    "code": code,
                },
            )
            token_response.raise_for_status()
            profile = await client.get(
                "https://graph.facebook.com/me",
                params={"fields": "id,name,email", "access_token": token_response.json()["access_token"]},
            )
        profile.raise_for_status()
    data = profile.json()
    if not data.get("email"):
        raise ValueError("OAuth provider did not return an email address")
    return {"email": data["email"], "full_name": data.get("name") or data.get("given_name") or "OAuth User"}
