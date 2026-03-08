from __future__ import annotations

import json
import random
from pathlib import Path

from runtime.glyphser.checkpoint.migrate_checkpoint import checkpoint_migrate
from runtime.glyphser.checkpoint.restore import restore_checkpoint
from runtime.glyphser.trace.migrate_trace import migrate_trace


def _rand_value(rng: random.Random, depth: int = 0):
    if depth >= 3:
        return rng.choice([None, True, False, rng.randint(-100, 100), rng.random(), f"v{rng.randint(0, 999)}"])
    choice = rng.randrange(0, 4)
    if choice == 0:
        return rng.choice([None, True, False, rng.randint(-100, 100), rng.random(), f"v{rng.randint(0, 999)}"])
    if choice == 1:
        return [_rand_value(rng, depth + 1) for _ in range(rng.randrange(0, 5))]
    return {f"k{i}": _rand_value(rng, depth + 1) for i in range(rng.randrange(0, 5))}


def test_checkpoint_restore_migrate_fuzz(tmp_path: Path) -> None:
    rng = random.Random(731)
    valid_state = {"weights": [1, 2, 3], "meta": {"epoch": 1}}

    good_file = tmp_path / "good.json"
    good_file.write_text(json.dumps(valid_state), encoding="utf-8")

    for _ in range(400):
        raw = _rand_value(rng)
        req = raw if isinstance(raw, dict) else {"state": raw}

        try:
            checkpoint_migrate(req)
        except ValueError:
            pass

        try:
            restore_checkpoint(req)
        except (ValueError, OSError, json.JSONDecodeError, TypeError):
            pass

    assert restore_checkpoint({"path": str(good_file)})["state"] == valid_state


def test_trace_migration_fuzz() -> None:
    rng = random.Random(181)
    for _ in range(400):
        raw = _rand_value(rng)
        req = raw if isinstance(raw, dict) else {"trace": raw}
        try:
            out = migrate_trace(req)
            assert out.get("status") == "OK"
        except ValueError:
            pass
