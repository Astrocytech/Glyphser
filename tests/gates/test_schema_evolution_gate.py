from __future__ import annotations

import json
from pathlib import Path

from tooling.quality_gates import schema_evolution_gate

ROOT = Path(__file__).resolve().parents[2]


def test_schema_evolution_gate_passes():
    report = schema_evolution_gate.evaluate()
    assert report["status"] == "PASS"
    emitted = json.loads((ROOT / "evidence" / "gates" / "quality" / "schema_evolution.json").read_text(encoding="utf-8"))
    assert emitted["status"] == "PASS"
