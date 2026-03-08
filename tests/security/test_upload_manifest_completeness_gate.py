from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, sign_file
from tooling.security import upload_manifest_completeness_gate, upload_manifest_generate


def test_upload_manifest_generate_and_gate_pass(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    gov = repo / "governance" / "security"
    sec.mkdir(parents=True)
    gov.mkdir(parents=True)
    (gov / "advanced_hardening_policy.json").write_text(
        json.dumps({"security_workflow_evidence_required": ["security_super_gate.json"]}) + "\n",
        encoding="utf-8",
    )
    (sec / "security_super_gate.json").write_text(
        json.dumps({"status": "PASS", "findings": [], "summary": {}, "metadata": {}}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(upload_manifest_generate, "ROOT", repo)
    monkeypatch.setattr(upload_manifest_generate, "evidence_root", lambda: repo / "evidence")
    assert upload_manifest_generate.main([]) == 0

    monkeypatch.setattr(upload_manifest_completeness_gate, "ROOT", repo)
    monkeypatch.setattr(upload_manifest_completeness_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(
        upload_manifest_completeness_gate,
        "load_policy",
        lambda: {"security_workflow_evidence_required": ["security_super_gate.json"]},
    )
    assert upload_manifest_completeness_gate.main([]) == 0


def test_upload_manifest_gate_fails_on_missing_required(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    manifest = sec / "upload_manifest.json"
    manifest.write_text(
        json.dumps({"status": "PASS", "findings": [], "summary": {"artifacts": []}, "metadata": {}}) + "\n",
        encoding="utf-8",
    )
    manifest.with_suffix(".json.sig").write_text(sign_file(manifest, key=current_key(strict=False)) + "\n", encoding="utf-8")
    monkeypatch.setattr(upload_manifest_completeness_gate, "ROOT", repo)
    monkeypatch.setattr(upload_manifest_completeness_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(
        upload_manifest_completeness_gate,
        "load_policy",
        lambda: {"security_workflow_evidence_required": ["security_super_gate.json"]},
    )
    assert upload_manifest_completeness_gate.main([]) == 1
    report = json.loads((sec / "upload_manifest_completeness_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert "manifest_missing_required_artifact:security_super_gate.json" in report["findings"]
