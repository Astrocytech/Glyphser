from __future__ import annotations

import json
from pathlib import Path

from tooling.quality_gates import determinism_matrix_gate

ROOT = Path(__file__).resolve().parents[2]


def test_determinism_matrix_gate_passes():
    report = determinism_matrix_gate.evaluate()
    assert report["status"] == "PASS"
    emitted = json.loads((ROOT / "evidence" / "gates" / "quality" / "determinism_matrix.json").read_text(encoding="utf-8"))
    assert emitted["status"] == "PASS"
