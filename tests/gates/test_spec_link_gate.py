from __future__ import annotations

import json
from pathlib import Path

from tooling.quality_gates import spec_link_gate

ROOT = Path(__file__).resolve().parents[2]


def test_spec_link_gate_passes() -> None:
    report = spec_link_gate.evaluate()
    assert report["status"] == "PASS"
    report = json.loads((ROOT / "evidence" / "gates" / "structure" / "spec_link_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
