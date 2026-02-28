from __future__ import annotations

import json
from pathlib import Path

from src.glyphser.generated import bindings as gen_bindings

ROOT = Path(__file__).resolve().parents[1]
TRACE = ROOT / "artifacts" / "inputs" / "fixtures" / "replay-determinism" / "trace.json"
EXPECTED = ROOT / "artifacts" / "expected" / "goldens" / "replay-determinism" / "replay_expected.json"


def test_replay_compare_trace_matches():
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
    result = gen_bindings.replay_compare_trace(TRACE, TRACE)
    assert result == expected
