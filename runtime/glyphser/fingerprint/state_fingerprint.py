"""Deterministic state fingerprint helper."""
from __future__ import annotations

import hashlib
from typing import Any, Dict

from runtime.glyphser.serialization.canonical_cbor import encode_canonical


def state_fingerprint(payload: Dict[str, Any]) -> str:
    return hashlib.sha256(encode_canonical(payload)).hexdigest()
