"""Authentication orchestration and secure refresh-token rotation."""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

from app.core.config.settings import get_settings
from app.core.security.auth import create_token
from app.core.security.password import hash_password


def hash_refresh_token(token: str) -> str:
    """Return the SHA-256 digest persisted for a raw refresh bearer token."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def issue_tokens(user_id: UUID) -> tuple[str, str, str, datetime]:
    """Issue short-lived access and opaque refresh credentials.

    The returned digest is the only refresh value suitable for persistence.
    """
    settings = get_settings()
    raw_refresh = secrets.token_urlsafe(48)
    expiry = datetime.now(UTC) + timedelta(days=settings.refresh_token_days)
    access = create_token(user_id, "access", timedelta(minutes=settings.access_token_minutes))
    return access, raw_refresh, hash_refresh_token(raw_refresh), expiry


def issue_password_hash(password: str) -> str:
    """Hash a password for reset and social-account provisioning workflows."""
    return hash_password(password)
