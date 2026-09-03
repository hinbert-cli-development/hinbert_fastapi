"""Password hashing using bcrypt through Passlib.

Only password hashes are persisted; plaintext passwords are never logged or
returned. Replace the scheme configuration here if an enterprise KMS policy
requires a different approved password verifier.
"""

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password with bcrypt and return the encoded hash."""
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Constant-time verify a candidate password against its stored hash."""
    return pwd_context.verify(password, password_hash)
