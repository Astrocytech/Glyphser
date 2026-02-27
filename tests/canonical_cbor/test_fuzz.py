"""Deterministic fuzz/property tests for canonical CBOR."""

from __future__ import annotations

import random

from src.glyphser.serialization.canonical_cbor import encode_canonical_hex


SEED = 1337


def _rand_str(rng: random.Random) -> str:
    alphabet = "abc123"
    return "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 6)))


def _rand_bytes(rng: random.Random) -> bytes:
    return bytes(rng.getrandbits(8) for _ in range(rng.randint(0, 6)))


def _rand_obj(rng: random.Random, depth: int) -> object:
    if depth <= 0:
        choice = rng.randint(0, 4)
        if choice == 0:
            return rng.randint(-10, 10)
        if choice == 1:
            return _rand_str(rng)
        if choice == 2:
            return _rand_bytes(rng)
        if choice == 3:
            return True
        return False

    choice = rng.randint(0, 5)
    if choice == 0:
        return rng.randint(-100, 100)
    if choice == 1:
        return _rand_str(rng)
    if choice == 2:
        return _rand_bytes(rng)
    if choice == 3:
        return [_rand_obj(rng, depth - 1) for _ in range(rng.randint(0, 4))]
    if choice == 4:
        # dict with string keys to avoid unsupported keys
        d = {}
        for _ in range(rng.randint(0, 4)):
            d[_rand_str(rng)] = _rand_obj(rng, depth - 1)
        return d
    return None


def _shuffle_dict(rng: random.Random, d: dict) -> dict:
    items = list(d.items())
    rng.shuffle(items)
    return {k: v for k, v in items}


def test_canonical_cbor_determinism_repeatable():
    rng = random.Random(SEED)
    for _ in range(200):
        obj = _rand_obj(rng, depth=3)
        a = encode_canonical_hex(obj)
        b = encode_canonical_hex(obj)
        assert a == b


def test_canonical_cbor_dict_order_independent():
    rng = random.Random(SEED)
    for _ in range(100):
        base = {}
        for _ in range(rng.randint(1, 6)):
            base[_rand_str(rng)] = _rand_obj(rng, depth=2)
        shuffled = _shuffle_dict(rng, base)
        assert encode_canonical_hex(base) == encode_canonical_hex(shuffled)
