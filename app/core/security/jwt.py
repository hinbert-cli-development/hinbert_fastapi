"""JWT access-token creation and validation.

Access tokens are short-lived and carry only a subject and token type. Refresh
tokens are generated separately and must be hashed before database persistence.
"""

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from jose import JWTError, jwt

from app.core.config.settings import get_settings


def create_token(subject: UUID | str, token_type: str, expires_delta: timedelta) -> str:
    """Create a signed JWT for a subject and explicit token type."""
    now = datetime.now(UTC)
    payload: dict[str, Any] = {"sub": str(subject), "type": token_type, "iat": now, "exp": now + expires_delta}
    settings = get_settings()
    return jwt.encode(payload, settings.jwt_secret_key.get_secret_value(), algorithm=settings.jwt_algorithm)


def decode_token(token: str, expected_type: str = "access") -> dict[str, Any]:
    """Decode and validate a JWT, raising ``ValueError`` for invalid tokens."""
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret_key.get_secret_value(), algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise ValueError("Invalid or expired token") from exc
    if payload.get("type") != expected_type or not payload.get("sub"):
        raise ValueError("Invalid token type")
    return payload
