"""HMAC signing helpers for evidence/provenance artifacts."""

from __future__ import annotations

import hashlib
import hmac
import os
from pathlib import Path

_KEY_ENV = "GLYPHSER_PROVENANCE_HMAC_KEY"
_FALLBACK_KEY = "glyphser-provenance-hmac-fallback-v1"
_STRICT_ENV = "GLYPHSER_REQUIRE_SIGNING_KEY"
_ENV_HINT = "GLYPHSER_ENV"


def current_key(*, strict: bool = False) -> bytes:
    raw = os.environ.get(_KEY_ENV, "")
    require_key = strict or os.environ.get(_STRICT_ENV, "").strip().lower() in {"1", "true", "yes"}
    env_hint = os.environ.get(_ENV_HINT, "").strip().lower()
    if env_hint in {"ci", "prod", "production", "release"}:
        require_key = True
    if not raw:
        if require_key:
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
