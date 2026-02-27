"""Canonical CBOR vector tests."""

from __future__ import annotations

from .vector_loader import load_vectors
from src.glyphser.serialization.canonical_cbor import encode_canonical_hex, validate_canonical_hex


def _materialize_input(raw):
    if isinstance(raw, dict):
        if "__bytes__" in raw:
            return bytes.fromhex(raw["__bytes__"])
        if "__map__" in raw:
            # Preserve ordering to test canonical sorting.
            return {k: v for k, v in raw["__map__"]}
    return raw


def test_canonical_cbor_vectors():
    data = load_vectors()
    for vector in data["vectors"]:
        obj = _materialize_input(vector["input_json"])
        expected = vector["expected_cbor_hex"]
        validate_canonical_hex(obj, expected)
        actual = encode_canonical_hex(obj)
        assert actual == expected, vector["id"]
