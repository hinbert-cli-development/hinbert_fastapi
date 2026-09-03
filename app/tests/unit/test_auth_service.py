"""Unit tests for token hashing and issuance primitives."""

from uuid import uuid4

from app.services.auth_service import hash_refresh_token, issue_tokens


def test_refresh_hash_is_deterministic_and_not_plaintext():
    """The database representation is fixed-length SHA-256, never the bearer value."""
    assert hash_refresh_token("secret") == hash_refresh_token("secret")
    assert hash_refresh_token("secret") != "secret"


def test_issue_tokens_returns_access_and_opaque_refresh():
    """Token issuance returns independently usable values."""
    access, refresh, digest, expiry = issue_tokens(uuid4())
    assert access and refresh and digest and expiry
    assert digest == hash_refresh_token(refresh)
