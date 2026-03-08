from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUITE = ROOT / "artifacts" / "inputs" / "fixtures" / "replay-suite-1" / "trace.json"
EXPECTED = ROOT / "artifacts" / "expected" / "goldens" / "replay-suite-1" / "trace_expected.json"


def test_replay_suite_1():
    payload = json.loads(SUITE.read_text(encoding="utf-8"))
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))

    trace_hash = (
        __import__("hashlib").sha256(json.dumps(payload["records"], sort_keys=True).encode("utf-8")).hexdigest()
    )
    checkpoint_hash = (
        __import__("hashlib").sha256(json.dumps(payload["checkpoint"], sort_keys=True).encode("utf-8")).hexdigest()
    )

    assert trace_hash == expected["trace_hash"]
    assert checkpoint_hash == expected["checkpoint_hash"]
