from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import bootstrap_key, current_key, verify_file

ROOT = Path(__file__).resolve().parents[2]


def test_timestamp_authority_readiness_checklist_exists_with_required_sections() -> None:
    checklist = ROOT / "governance" / "security" / "TIMESTAMP_AUTHORITY_READINESS_CHECKLIST.md"
    text = checklist.read_text(encoding="utf-8")
    assert "# Signed Timestamp Authority Integration Readiness Checklist" in text
    assert "## Control Checklist" in text
    assert "## Required Pre-Enablement Evidence" in text
    assert "## Rollout Guardrails" in text


def test_timestamp_authority_readiness_metadata_is_signed() -> None:
    meta = ROOT / "governance" / "security" / "metadata" / "TIMESTAMP_AUTHORITY_READINESS_CHECKLIST.meta.json"
    sig = meta.with_suffix(".json.sig")
    payload = json.loads(meta.read_text(encoding="utf-8"))
    assert payload["title"] == "Signed Timestamp Authority Integration Readiness Checklist"
    sig_text = sig.read_text(encoding="utf-8").strip()
    assert verify_file(meta, sig_text, key=current_key(strict=False)) or verify_file(meta, sig_text, key=bootstrap_key())
