from __future__ import annotations

import json
from pathlib import Path

from tooling.release.generate_traceability_index import generate

ROOT = Path(__file__).resolve().parents[2]


def test_generate_traceability_index_emits_index():
    payload = generate()
    assert payload["schema_version"] == "glyphser-traceability-index.v1"
    assert "git_commit" in payload
    out = json.loads((ROOT / "evidence" / "traceability" / "index.json").read_text(encoding="utf-8"))
    assert out["schema_version"] == "glyphser-traceability-index.v1"
