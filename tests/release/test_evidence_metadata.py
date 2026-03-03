from __future__ import annotations

import json
from pathlib import Path

from tooling.quality_gates.evidence_metadata_gate import evaluate
from tooling.release.generate_evidence_metadata import generate

ROOT = Path(__file__).resolve().parents[2]


def test_evidence_metadata_generate_and_validate():
    payload = generate()
    assert payload["schema_version"] == "glyphser-evidence-catalog.v1"

    report = evaluate()
    assert report["status"] == "PASS"

    out = json.loads((ROOT / "evidence" / "metadata" / "catalog.json").read_text(encoding="utf-8"))
    assert out["schema_version"] == "glyphser-evidence-catalog.v1"
