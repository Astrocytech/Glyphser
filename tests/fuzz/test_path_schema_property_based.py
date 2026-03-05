from __future__ import annotations

import random

import pytest

from runtime.glyphser.api.runtime_api import _validate_against_schema
from runtime.glyphser.security.path_guard import validate_path_text


def test_path_validator_property_rejects_traversal_and_confusables() -> None:
    rng = random.Random(20260305)
    bad_suffixes = [
        "../x.json",
        "..\\x.json",
        "safe/\uFF0E\uFF0E/out.json",
        "safe/\u2215/out.json",
    ]
    for _ in range(400):
        prefix = f"seg{rng.randrange(0, 99)}"
        tail = rng.choice(bad_suffixes)
        with pytest.raises(ValueError):
            validate_path_text(f"{prefix}/{tail}", field_name="path")


def test_path_validator_property_accepts_safe_json_like_paths() -> None:
    rng = random.Random(20260306)
    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789_-"
    for _ in range(400):
        depth = rng.randrange(1, 5)
        parts = []
        for _ in range(depth):
            ln = rng.randrange(1, 12)
            parts.append("".join(rng.choice(alphabet) for _ in range(ln)))
        candidate = "/".join(parts) + ".json"
        normalized = validate_path_text(candidate, field_name="path")
        assert normalized.endswith(".json")
        assert ".." not in normalized


def test_runtime_schema_property_rejects_unknown_submit_fields() -> None:
    rng = random.Random(20260307)
    base = {
        "payload": {"x": 1},
        "token": "token-a",
        "scope": "jobs:write",
        "idempotency_key": "",
    }
    for _ in range(300):
        candidate = dict(base)
        candidate[f"extra_{rng.randrange(0, 999)}"] = "boom"
        with pytest.raises(ValueError):
            _validate_against_schema("submit_request", candidate)
