from __future__ import annotations

import json
from pathlib import Path

from tooling.quality_gates import interface_stability_gate

ROOT = Path(__file__).resolve().parents[2]


def test_interface_stability_gate_passes():
    report = interface_stability_gate.evaluate()
    assert report["status"] == "PASS"
    emitted = json.loads(
        (ROOT / "evidence" / "gates" / "quality" / "interface_stability.json").read_text(encoding="utf-8")
    )
    assert emitted["status"] == "PASS"
