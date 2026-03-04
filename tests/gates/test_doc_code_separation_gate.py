from __future__ import annotations

import json
from pathlib import Path

from tooling.quality_gates import doc_code_separation_gate

ROOT = Path(__file__).resolve().parents[2]


def test_doc_code_separation_gate_passes():
    report = doc_code_separation_gate.evaluate()
    assert report["status"] == "PASS"
    latest = json.loads((ROOT / "evidence" / "gates" / "structure" / "latest.json").read_text(encoding="utf-8"))
    assert latest["status"] == "PASS"
