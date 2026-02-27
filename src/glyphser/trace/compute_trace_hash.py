"""Compute deterministic trace hash-chain."""
from __future__ import annotations

import hashlib
from typing import Any, Iterable

from src.glyphser.serialization.canonical_cbor import encode_canonical


def _sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def compute_trace_hash(records: Iterable[dict[str, Any]]) -> str:
    h = _sha256(encode_canonical(["trace_chain", []]))
    for record in records:
        record_hash = _sha256(encode_canonical(record))
        h = _sha256(encode_canonical(["trace_chain", [h, record_hash]]))
    return h.hex()
