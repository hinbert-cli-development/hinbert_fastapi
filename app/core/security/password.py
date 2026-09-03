"""Password hashing using bcrypt through Passlib.

Only password hashes are persisted; plaintext passwords are never logged or
returned. Replace the scheme configuration here if an enterprise KMS policy
requires a different approved password verifier.
"""

import bcrypt


def hash_password(password: str) -> str:
    """Hash a password with bcrypt and return the encoded hash."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Constant-time verify a candidate password against its stored hash."""
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
