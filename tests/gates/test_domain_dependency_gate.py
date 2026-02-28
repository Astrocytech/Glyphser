from __future__ import annotations

import json
from pathlib import Path
from tooling.quality_gates import domain_dependency_gate

ROOT = Path(__file__).resolve().parents[2]


def test_domain_dependency_gate_passes() -> None:
    report = domain_dependency_gate.evaluate()
    assert report["status"] == "PASS"
    persisted = json.loads((ROOT / "evidence" / "gates" / "structure" / "domain_dependency_gate.json").read_text(encoding="utf-8"))
    assert persisted["status"] == "PASS"
