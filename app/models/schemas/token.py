"""Token exchange schemas."""

from pydantic import BaseModel


class TokenResponse(BaseModel):
    """Bearer access token plus opaque refresh token."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    """Raw refresh token accepted only over TLS."""

    refresh_token: str
