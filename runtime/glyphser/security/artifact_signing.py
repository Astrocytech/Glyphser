"""HMAC signing helpers for evidence/provenance artifacts."""

from __future__ import annotations

import hashlib
import hmac
import os
from pathlib import Path

_KEY_ENV = "GLYPHSER_PROVENANCE_HMAC_KEY"
_FALLBACK_KEY = "glyphser-provenance-hmac-fallback-v1"


def current_key(*, strict: bool = False) -> bytes:
    raw = os.environ.get(_KEY_ENV, "")
    if not raw:
        if strict:
            raise ValueError(f"missing required signing key env: {_KEY_ENV}")
        raw = _FALLBACK_KEY
    return raw.encode("utf-8")


def sign_bytes(payload: bytes, *, key: bytes) -> str:
    return hmac.new(key, payload, hashlib.sha256).hexdigest()


def sign_file(path: Path, *, key: bytes) -> str:
    return sign_bytes(path.read_bytes(), key=key)


def verify_file(path: Path, signature_hex: str, *, key: bytes) -> bool:
    expected = sign_file(path, key=key)
    return hmac.compare_digest(expected, signature_hex.strip())
