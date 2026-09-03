"""Small authentication primitives shared by services and dependencies."""

from app.core.security.password import verify_password


def authenticate_password(password: str, password_hash: str) -> bool:
    """Return whether credentials match without exposing password details."""
    return verify_password(password, password_hash)
