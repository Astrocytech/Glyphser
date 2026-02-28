from __future__ import annotations

import json
import random

import pytest

from runtime.glyphser.checkpoint.restore import restore_checkpoint


def _random_checkpoint(seed: int) -> dict:
    rng = random.Random(seed)
    return {
        "checkpoint_id": f"ckpt-{seed}",
        "global_step": rng.randrange(0, 1000),
        "manifest_hash": f"hash-{seed}",
    }


def test_checkpoint_restore_fuzz(tmp_path):
    for seed in range(10):
        payload = _random_checkpoint(seed)
        path = tmp_path / f"ckpt-{seed}.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        result = restore_checkpoint({"path": str(path)})
        assert result["state"] == payload
