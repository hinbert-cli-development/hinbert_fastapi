"""Unit tests for authentication and credential primitives."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from app.core.security.jwt import create_token, decode_token
from app.core.security.password import hash_password, verify_password
from app.services.auth_service import hash_refresh_token, issue_tokens


def test_refresh_hash_is_deterministic_and_not_plaintext():
    """The database representation is fixed-length SHA-256, never the bearer value."""
    assert hash_refresh_token("secret") == hash_refresh_token("secret")
    assert hash_refresh_token("secret") != "secret"


def test_issue_tokens_returns_matching_refresh_digest():
    """Token issuance returns independently usable values and a matching digest."""
    access, refresh, digest, expiry = issue_tokens(uuid4())
    assert access and refresh and digest and expiry > datetime.now(UTC)
    assert digest == hash_refresh_token(refresh)


def test_access_token_contains_subject_and_type():
    """JWT claims identify the subject and prevent refresh-token confusion."""
    subject = uuid4()
    token = create_token(subject, "access", timedelta(minutes=5))
    claims = decode_token(token)
    assert claims["sub"] == str(subject)
    assert claims["type"] == "access"


def test_wrong_token_type_is_rejected():
    """A token issued for one purpose cannot be used for another purpose."""
    token = create_token(uuid4(), "refresh", timedelta(minutes=5))
    with pytest.raises(ValueError):
        decode_token(token)


def test_password_hash_is_salted_and_verifiable():
    """Two hashes differ because bcrypt salts each password independently."""
    first = hash_password("StrongPassword!123")
    second = hash_password("StrongPassword!123")
    assert first != second
    assert verify_password("StrongPassword!123", first)
    assert not verify_password("wrong", first)
