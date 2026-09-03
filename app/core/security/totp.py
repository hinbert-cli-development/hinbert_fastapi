"""TOTP primitives for optional multi-factor authentication."""

import pyotp


def new_secret() -> str:
    """Generate a cryptographically random Base32 TOTP secret."""
    return pyotp.random_base32()


def verify_code(secret: str, code: str) -> bool:
    """Verify a current TOTP code with a small clock-skew window."""
    return bool(pyotp.TOTP(secret).verify(code, valid_window=1))
