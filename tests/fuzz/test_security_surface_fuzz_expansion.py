from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

from runtime.glyphser.api.validate_signature import validate_api_signature
from runtime.glyphser.checkpoint.migrate_checkpoint import checkpoint_migrate
from runtime.glyphser.checkpoint.restore import restore_checkpoint
from runtime.glyphser.trace.migrate_trace import migrate_trace


def _rand_json(rng: random.Random, depth: int = 0) -> Any:
    if depth >= 4:
        return rng.choice([None, True, False, rng.randint(-99, 99), rng.random(), f"s{rng.randint(0, 999)}"])
    choice = rng.randrange(0, 5)
    if choice <= 1:
        return rng.choice([None, True, False, rng.randint(-99, 99), rng.random(), f"s{rng.randint(0, 999)}"])
    if choice == 2:
        return [_rand_json(rng, depth + 1) for _ in range(rng.randrange(0, 6))]
    return {f"k{ix}": _rand_json(rng, depth + 1) for ix in range(rng.randrange(0, 6))}


def test_validate_signature_mutation_fuzz_loop() -> None:
    rng = random.Random(4301)
    allowed = ["Glyphser.Model.Forward", "Glyphser.Trace.TraceMigrate"]
    base = {
        "operator_id": "Glyphser.Model.Forward",
        "version": "1.0.0",
        "method": "POST",
        "surface": "runtime_api",
        "request_schema_digest": "sha256:abc",
        "response_schema_digest": "sha256:def",
    }
    for _ in range(600):
        case = dict(base)
        case[str(rng.randrange(0, 20))] = _rand_json(rng)
        if rng.random() < 0.4:
            case["operator_id"] = str(_rand_json(rng))
        if rng.random() < 0.4:
            case["request_schema_digest"] = str(_rand_json(rng))
        if rng.random() < 0.4:
            case["response_schema_digest"] = str(_rand_json(rng))
        try:
            validate_api_signature(case, allowed_ops=allowed)
        except (TypeError, ValueError):
            pass


def test_checkpoint_trace_path_fuzz_loop(tmp_path: Path) -> None:
    rng = random.Random(4302)
    good = tmp_path / "good.json"
    good.write_text(json.dumps({"state": {"v": [1, 2, 3]}}), encoding="utf-8")

    for _ in range(600):
        raw = _rand_json(rng)
        req = raw if isinstance(raw, dict) else {"state": raw}
        if isinstance(req, dict) and rng.random() < 0.3:
            req["path"] = str(tmp_path / f"{rng.randrange(0, 5)}.json")
        if isinstance(req, dict) and rng.random() < 0.2:
            req["allowed_root"] = str(tmp_path)
        try:
            checkpoint_migrate(req)
        except ValueError:
            pass
        try:
            restore_checkpoint(req)
        except (ValueError, OSError, TypeError, json.JSONDecodeError):
            pass
        try:
            out = migrate_trace(req if isinstance(req, dict) else {"trace": req})
            assert out.get("status") == "OK"
        except ValueError:
            pass

    out = restore_checkpoint({"path": str(good)})
    assert isinstance(out.get("state"), dict)
