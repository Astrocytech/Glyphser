"""Canonical CBOR encoding (minimal, deterministic subset)."""
from __future__ import annotations

import struct
from typing import Any


def _enc_uint(major: int, n: int) -> bytes:
    if n < 0:
        raise ValueError("negative uint")
    if n < 24:
        return bytes([(major << 5) | n])
    if n < 256:
        return bytes([(major << 5) | 24, n])
    if n < 65536:
        return bytes([(major << 5) | 25]) + n.to_bytes(2, "big")
    if n < 4294967296:
        return bytes([(major << 5) | 26]) + n.to_bytes(4, "big")
    return bytes([(major << 5) | 27]) + n.to_bytes(8, "big")


def encode_canonical(obj: Any) -> bytes:
    if obj is None:
        return b"\xf6"
    if obj is False:
        return b"\xf4"
    if obj is True:
        return b"\xf5"
    if isinstance(obj, int):
        if obj >= 0:
            return _enc_uint(0, obj)
        return _enc_uint(1, -1 - obj)
    if isinstance(obj, bytes):
        return _enc_uint(2, len(obj)) + obj
    if isinstance(obj, str):
        b = obj.encode("utf-8")
        return _enc_uint(3, len(b)) + b
    if isinstance(obj, float):
        return b"\xfb" + struct.pack(">d", obj)
    if isinstance(obj, (list, tuple)):
        out = [_enc_uint(4, len(obj))]
        for item in obj:
            out.append(encode_canonical(item))
        return b"".join(out)
    if isinstance(obj, dict):
        items = []
        for k, v in obj.items():
            kb = encode_canonical(k)
            vb = encode_canonical(v)
            items.append((kb, vb))
        items.sort(key=lambda kv: kv[0])
        out = [_enc_uint(5, len(items))]
        for kb, vb in items:
            out.append(kb)
            out.append(vb)
        return b"".join(out)
    raise TypeError(f"unsupported type: {type(obj)!r}")


def encode_canonical_hex(obj: Any) -> str:
    return encode_canonical(obj).hex()


def validate_canonical_hex(obj: Any, expected_hex: str) -> None:
    actual = encode_canonical_hex(obj)
    if actual != expected_hex:
        raise ValueError(f"cbor mismatch: expected={expected_hex} got={actual}")
