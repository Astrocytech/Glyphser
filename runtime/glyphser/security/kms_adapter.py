"""Optional KMS/HSM signing adapter.

This adapter is deterministic for local validation and can be replaced with a real
KMS/HSM integration by setting environment variables in CI/release.
"""

from __future__ import annotations

import hashlib
import hmac
import os

_KMS_KEY_ENV = "GLYPHSER_KMS_HMAC_KEY"


def sign_payload(payload: bytes) -> str:
    raw = os.environ.get(_KMS_KEY_ENV, "").strip()
    if not raw:
        raise ValueError(f"missing required KMS adapter key env: {_KMS_KEY_ENV}")
    return hmac.new(raw.encode("utf-8"), payload, hashlib.sha256).hexdigest()
