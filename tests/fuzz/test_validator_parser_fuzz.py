from __future__ import annotations

import random
from typing import Any

from runtime.glyphser._generated.validators import validate_ModelIRExecutorL2
from runtime.glyphser.api.validate_signature import validate_api_signature


def _rand_scalar(rng: random.Random) -> Any:
    choice = rng.randrange(0, 6)
    if choice == 0:
        return None
    if choice == 1:
        return bool(rng.randrange(0, 2))
    if choice == 2:
        return rng.randint(-1000, 1000)
    if choice == 3:
        return rng.random() * 1000.0
    if choice == 4:
        return f"s{rng.randrange(0, 100000)}"
    return {"nested": rng.randrange(0, 9)}


def _rand_json(rng: random.Random, depth: int = 0) -> Any:
    if depth >= 3:
        return _rand_scalar(rng)
    choice = rng.randrange(0, 4)
    if choice == 0:
        return _rand_scalar(rng)
    if choice == 1:
        return [_rand_json(rng, depth + 1) for _ in range(rng.randrange(0, 4))]
    return {f"k{ix}": _rand_json(rng, depth + 1) for ix in range(rng.randrange(0, 5))}


def test_generated_validator_never_crashes() -> None:
    rng = random.Random(1337)
    for _ in range(300):
        payload = _rand_json(rng)
        obj = payload if isinstance(payload, dict) else {"payload": payload}
        errors = validate_ModelIRExecutorL2(obj)
        assert isinstance(errors, list)
        assert all(isinstance(err, str) for err in errors)


def test_api_signature_validator_handles_fuzzed_payloads() -> None:
    rng = random.Random(2026)
    for _ in range(300):
        raw = _rand_json(rng)
        record = raw if isinstance(raw, dict) else {"payload": raw}
        try:
            validate_api_signature(record, allowed_ops=["Glyphser.Data.NextBatch"])
        except (TypeError, ValueError):
            # Invalid records are expected; this test enforces parser safety (no unexpected exceptions).
            pass
