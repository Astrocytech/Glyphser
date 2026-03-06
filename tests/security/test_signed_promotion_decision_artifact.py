from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, verify_file
from tooling.security import signed_promotion_decision_artifact


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_signed_promotion_decision_artifact_passes_with_approval_chain(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write(repo / "evidence" / "security" / "promotion_go_no_go_report.json", {"summary": {"decision": "GO"}, "findings": []})

    monkeypatch.setattr(signed_promotion_decision_artifact, "ROOT", repo)
    monkeypatch.setattr(signed_promotion_decision_artifact, "GO_NO_GO", repo / "evidence/security/promotion_go_no_go_report.json")
    monkeypatch.setattr(signed_promotion_decision_artifact, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_BYPASSED_BLOCKERS", "")
    monkeypatch.setenv("GLYPHSER_APPROVAL_CHAIN", '["security-lead","release-manager"]')
    monkeypatch.setenv("GLYPHSER_RUN_ID", "run-123")
    monkeypatch.setenv("GLYPHSER_EVIDENCE_BUNDLE_DIGEST", "sha256:" + "a" * 64)

    assert signed_promotion_decision_artifact.main([]) == 0
    artifact = repo / "evidence" / "security" / "promotion_decision_artifact.json"
    sig = (repo / "evidence" / "security" / "promotion_decision_artifact.json.sig").read_text(encoding="utf-8").strip()
    payload = json.loads(artifact.read_text(encoding="utf-8"))
    assert payload["immutable_run_id"] == "run-123"
    assert payload["immutable_evidence_digest"] == "sha256:" + "a" * 64
    assert verify_file(artifact, sig, key=current_key(strict=False))


def test_signed_promotion_decision_artifact_fails_on_unmatched_bypass(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write(
        repo / "evidence" / "security" / "promotion_go_no_go_report.json",
        {"summary": {"decision": "NO_GO"}, "findings": ["mandatory_control_not_pass:super:WARN"]},
    )

    monkeypatch.setattr(signed_promotion_decision_artifact, "ROOT", repo)
    monkeypatch.setattr(signed_promotion_decision_artifact, "GO_NO_GO", repo / "evidence/security/promotion_go_no_go_report.json")
    monkeypatch.setattr(signed_promotion_decision_artifact, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_BYPASSED_BLOCKERS", '["nonexistent_blocker"]')
    monkeypatch.setenv("GLYPHSER_APPROVAL_CHAIN", '["security-lead","release-manager"]')
    monkeypatch.setenv("GLYPHSER_RUN_ID", "run-123")
    monkeypatch.setenv("GLYPHSER_EVIDENCE_BUNDLE_DIGEST", "sha256:" + "b" * 64)

    assert signed_promotion_decision_artifact.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "signed_promotion_decision_artifact_gate.json").read_text(encoding="utf-8"))
    assert any(str(item).startswith("bypassed_blockers_not_in_go_no_go_report:") for item in report["findings"])


def test_signed_promotion_decision_artifact_fails_without_immutable_references(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write(repo / "evidence" / "security" / "promotion_go_no_go_report.json", {"summary": {"decision": "GO"}, "findings": []})

    monkeypatch.setattr(signed_promotion_decision_artifact, "ROOT", repo)
    monkeypatch.setattr(signed_promotion_decision_artifact, "GO_NO_GO", repo / "evidence/security/promotion_go_no_go_report.json")
    monkeypatch.setattr(signed_promotion_decision_artifact, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_BYPASSED_BLOCKERS", "")
    monkeypatch.setenv("GLYPHSER_APPROVAL_CHAIN", '["security-lead","release-manager"]')
    monkeypatch.delenv("GLYPHSER_RUN_ID", raising=False)
    monkeypatch.delenv("GITHUB_RUN_ID", raising=False)
    monkeypatch.delenv("GLYPHSER_EVIDENCE_BUNDLE_DIGEST", raising=False)

    assert signed_promotion_decision_artifact.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "signed_promotion_decision_artifact_gate.json").read_text(encoding="utf-8"))
    assert "missing_immutable_run_id" in report["findings"]
    assert "missing_immutable_evidence_digest" in report["findings"]
