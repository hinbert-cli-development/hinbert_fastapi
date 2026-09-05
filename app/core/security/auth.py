"""Small authentication primitives shared by services and dependencies."""

from app.core.security.password import verify_password
from app.core.security.jwt import decode_token

def create_token(subject, token_type, expires_delta):
    """Create a token through the selected authentication boundary."""
    from app.core.security.jwt import create_token as jwt_create_token

    return jwt_create_token(subject, token_type, expires_delta)


def authenticate_password(password: str, password_hash: str) -> bool:
    """Return whether credentials match without exposing password details."""
    return verify_password(password, password_hash)
