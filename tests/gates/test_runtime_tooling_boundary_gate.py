from __future__ import annotations

import json
from pathlib import Path

from tooling.quality_gates import runtime_tooling_boundary_gate

ROOT = Path(__file__).resolve().parents[2]


def test_runtime_tooling_boundary_gate_passes():
    report = runtime_tooling_boundary_gate.evaluate()
    assert report["status"] == "PASS"
    emitted = json.loads((ROOT / "evidence" / "gates" / "quality" / "runtime_tooling_boundary.json").read_text(encoding="utf-8"))
    assert emitted["status"] == "PASS"
