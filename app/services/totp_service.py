"""Two-factor orchestration kept separate from HTTP handlers."""

from app.core.security.totp import new_secret, verify_code


def setup_totp() -> str:
    """Return a new secret to encrypt and associate with a user."""
    return new_secret()


def verify_totp(secret: str, code: str) -> bool:
    """Verify a user-provided current code."""
    return verify_code(secret, code)
