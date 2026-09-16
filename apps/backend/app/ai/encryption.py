"""Encryption helpers for stored provider keys (Fernet/AES-GCM via cryptography)."""

from __future__ import annotations

import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings

_salt = b"myaibuddy-key-salt-v1"


def _fernet() -> Fernet:
    secret = settings.JWT_SECRET_KEY or "dev-only-insecure-fallback"
    key = hashlib.pbkdf2_hmac("sha256", secret.encode(), _salt, 120_000, dklen=32)
    return Fernet(base64.urlsafe_b64encode(key))


def encrypt_secret(plaintext: str) -> bytes:
    return _fernet().encrypt(plaintext.encode())


def decrypt_secret(blob: bytes | None) -> str:
    if not blob:
        return ""
    try:
        return _fernet().decrypt(blob).decode()
    except InvalidToken as exc:
        raise ValueError("Unable to decrypt stored credential (key changed?)") from exc


def fingerprint(plaintext: str) -> str:
    if not plaintext:
        return ""
    return hashlib.sha256(plaintext.encode()).hexdigest()[:16]
