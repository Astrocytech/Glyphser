"""HMAC signing helpers for evidence/provenance artifacts."""

from __future__ import annotations

import hashlib
import hmac
import importlib
import os
from pathlib import Path
from typing import Any

from runtime.glyphser.security.zeroization import zeroize_bytearray

_KEY_ENV = "GLYPHSER_PROVENANCE_HMAC_KEY"
_FALLBACK_KEY = "glyphser-provenance-hmac-fallback-v1"
_STRICT_ENV = "GLYPHSER_REQUIRE_SIGNING_KEY"
_ENV_HINT = "GLYPHSER_ENV"
_ADAPTER_ENV = "GLYPHSER_SIGNING_ADAPTER"
_KEY_ID_ENV = "GLYPHSER_PROVENANCE_KEY_ID"


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


def bootstrap_key() -> bytes:
    return _FALLBACK_KEY.encode("utf-8")


def key_metadata(*, strict: bool = False) -> dict[str, Any]:
    raw = os.environ.get(_KEY_ENV, "")
    env_hint = os.environ.get(_ENV_HINT, "").strip().lower()
    require_key = strict or os.environ.get(_STRICT_ENV, "").strip().lower() in {"1", "true", "yes"}
    if env_hint in {"ci", "prod", "production", "release"}:
        require_key = True
    fallback_used = not raw and not require_key
    source = "env" if raw else ("fallback" if fallback_used else "missing")
    return {
        "source": source,
        "adapter": os.environ.get(_ADAPTER_ENV, "").strip().lower() or "hmac",
        "key_id": os.environ.get(_KEY_ID_ENV, "").strip() or "",
        "fallback_used": fallback_used,
    }


def sign_bytes(payload: bytes, *, key: bytes) -> str:
    adapter = os.environ.get(_ADAPTER_ENV, "").strip().lower() or "hmac"
    if adapter == "hmac":
        key_buf = bytearray(key)
        try:
            return hmac.new(bytes(key_buf), payload, hashlib.sha256).hexdigest()
        finally:
            zeroize_bytearray(key_buf)
    if adapter == "kms":
        module = importlib.import_module("runtime.glyphser.security.kms_adapter")
        signer = getattr(module, "sign_payload")
        return str(signer(payload))
    raise ValueError(f"unsupported signing adapter: {adapter}")


def sign_file(path: Path, *, key: bytes) -> str:
    return sign_bytes(path.read_bytes(), key=key)


def verify_file(path: Path, signature_hex: str, *, key: bytes) -> bool:
    expected = sign_file(path, key=key)
    return hmac.compare_digest(expected, signature_hex.strip())
