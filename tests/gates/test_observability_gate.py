from __future__ import annotations

import json
from pathlib import Path
from tooling.gates import observability_gate

ROOT = Path(__file__).resolve().parents[2]


def test_observability_gate_passes():
    report = observability_gate.evaluate()
    assert report["status"] == "PASS"
    latest = json.loads((ROOT / "evidence" / "observability" / "latest.json").read_text(encoding="utf-8"))
    assert latest["status"] == "PASS"
    assert latest["slo_overall"] == "PASS"
