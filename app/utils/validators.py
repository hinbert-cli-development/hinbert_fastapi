"""Reusable validation functions for values not covered by Pydantic fields."""

import re


def is_strong_password(password: str) -> bool:
    """Require upper, lower, digit, symbol, and a twelve-character minimum."""
    return len(password) >= 12 and bool(
        re.search(r"[A-Z]", password)
        and re.search(r"[a-z]", password)
        and re.search(r"\d", password)
        and re.search(r"[^A-Za-z0-9]", password)
    )
