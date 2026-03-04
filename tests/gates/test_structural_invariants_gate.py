from __future__ import annotations

import json
from pathlib import Path

from tooling.quality_gates import structural_invariants_gate

ROOT = Path(__file__).resolve().parents[2]


def test_structural_invariants_gate_passes() -> None:
    report = structural_invariants_gate.evaluate()
    assert report["status"] == "PASS"
    report = json.loads(
        (ROOT / "evidence" / "gates" / "structure" / "structural_invariants.json").read_text(encoding="utf-8")
    )
    assert report["status"] == "PASS"
