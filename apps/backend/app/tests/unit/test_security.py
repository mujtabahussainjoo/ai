"""Unit tests for password hashing and JWT lifecycle."""

from __future__ import annotations

import uuid

import jwt
import pytest

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_password_hash_roundtrip() -> None:
    hashed = hash_password("S3cretPass!")
    assert verify_password("S3cretPass!", hashed)
    assert not verify_password("wrong-pass", hashed)


def test_token_type_is_enforced() -> None:
    access = create_access_token(uuid.uuid4())
    refresh = create_refresh_token(uuid.uuid4())
    assert decode_token(access, expected_type="access")["type"] == "access"
    assert decode_token(refresh, expected_type="refresh")["type"] == "refresh"
    with pytest.raises(jwt.InvalidTokenError):
        decode_token(refresh, expected_type="access")


def test_access_token_embeds_subject_and_roles() -> None:
    subject = uuid.uuid4()
    token = create_access_token(subject, extra={"roles": ["user"]})
    payload = decode_token(token)
    assert payload["sub"] == str(subject)
    assert payload["roles"] == ["user"]
