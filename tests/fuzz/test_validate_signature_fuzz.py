from __future__ import annotations

import random

from runtime.glyphser.api.validate_signature import validate_api_signature


def _rand_value(rng: random.Random, depth: int = 0):
    if depth >= 3:
        return rng.choice([None, True, False, rng.randint(-9, 9), rng.random(), f"s{rng.randint(0, 99)}"])
    choice = rng.randrange(0, 4)
    if choice == 0:
        return rng.choice([None, True, False, rng.randint(-9, 9), rng.random(), f"s{rng.randint(0, 99)}"])
    if choice == 1:
        return [_rand_value(rng, depth + 1) for _ in range(rng.randrange(0, 4))]
    return {f"k{i}": _rand_value(rng, depth + 1) for i in range(rng.randrange(0, 4))}


def test_validate_signature_fuzz_loop() -> None:
    rng = random.Random(42024)
    allowed = ["Glyphser.Data.NextBatch", "Glyphser.Model.Forward"]
    for _ in range(500):
        raw = _rand_value(rng)
        record = raw if isinstance(raw, dict) else {"payload": raw}
        try:
            validate_api_signature(record, allowed_ops=allowed)
        except (TypeError, ValueError):
            pass
