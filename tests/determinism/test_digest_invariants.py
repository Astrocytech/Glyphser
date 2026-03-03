from __future__ import annotations

import random

from glyphser.internal.hashing import canonical_sha256
from glyphser.public.verify import verify


def _simple_model():
    return {
        "ir_hash": "invariant-ir",
        "nodes": [{"node_id": "x", "instr": "Input", "shape_out": [1], "dtype": "f32"}],
        "outputs": [{"node_id": "x", "output_idx": 0}],
    }


def test_same_payload_same_digest_property_style():
    model = _simple_model()
    rng = random.Random(7)
    for _ in range(50):
        value = rng.uniform(-100.0, 100.0)
        payload = {"x": [round(value, 8)]}
        a = verify(model, payload).digest
        b = verify(model, payload).digest
        assert a == b


def test_mutation_changes_digest_property_style():
    rng = random.Random(11)
    for _ in range(50):
        a = {"seed": 7, "value": round(rng.uniform(-10, 10), 6)}
        b = dict(a)
        b["seed"] = 99
        assert canonical_sha256(a) != canonical_sha256(b)
