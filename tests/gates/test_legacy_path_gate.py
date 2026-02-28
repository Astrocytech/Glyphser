from __future__ import annotations

import json
from pathlib import Path
from tooling.quality_gates import legacy_path_gate

ROOT = Path(__file__).resolve().parents[2]


def test_legacy_path_gate_passes() -> None:
    report = legacy_path_gate.evaluate()
    assert report["status"] == "PASS"
    report = json.loads((ROOT / "evidence" / "gates" / "structure" / "legacy_path_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
