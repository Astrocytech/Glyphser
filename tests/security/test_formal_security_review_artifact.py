from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, verify_file
from tooling.security import formal_security_review_artifact


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")


def test_formal_security_review_artifact_passes_and_is_signed(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    _write_json(sec / "security_super_gate.json", {"status": "PASS"})
    _write_json(sec / "security_verification_summary.json", {"status": "PASS"})
    _write_json(sec / "security_posture_executive_summary.json", {"status": "PASS"})
    _write_json(sec / "security_state_transition_invariants_gate.json", {"status": "PASS"})

    monkeypatch.setenv("GLYPHSER_SECURITY_OWNER", "security-owner@glyphser.local")
    monkeypatch.setattr(formal_security_review_artifact, "ROOT", repo)
    monkeypatch.setattr(formal_security_review_artifact, "evidence_root", lambda: repo / "evidence")
    assert formal_security_review_artifact.main([]) == 0

    report = sec / "formal_security_review_artifact.json"
    sig = sec / "formal_security_review_artifact.json.sig"
    assert report.exists()
    assert sig.exists()
    payload = json.loads(report.read_text(encoding="utf-8"))
    assert payload["status"] == "PASS"
    assert verify_file(report, sig.read_text(encoding="utf-8").strip(), key=current_key(strict=False))


def test_formal_security_review_artifact_fails_when_inputs_or_owner_missing(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    _write_json(sec / "security_super_gate.json", {"status": "PASS"})

    monkeypatch.delenv("GLYPHSER_SECURITY_OWNER", raising=False)
    monkeypatch.setattr(formal_security_review_artifact, "ROOT", repo)
    monkeypatch.setattr(formal_security_review_artifact, "evidence_root", lambda: repo / "evidence")
    assert formal_security_review_artifact.main([]) == 1
    payload = json.loads((sec / "formal_security_review_artifact.json").read_text(encoding="utf-8"))
    assert payload["status"] == "FAIL"
    assert any(str(item).startswith("missing_review_artifact:") for item in payload["findings"])
    assert "missing_env:GLYPHSER_SECURITY_OWNER" in payload["findings"]
