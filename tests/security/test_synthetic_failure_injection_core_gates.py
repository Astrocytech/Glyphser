from __future__ import annotations

import json
from pathlib import Path

from tooling.security import (
    policy_signature_gate,
    security_artifact_signature_coverage_gate,
    security_unsigned_json_gate,
    security_workflow_permissions_policy_gate,
)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_synthetic_failure_policy_signature_missing_sig(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "example_policy.json"
    _write_json(policy, {"ok": True})
    _write_json(repo / "governance" / "security" / "policy_signature_manifest.json", {"policies": [str(policy.relative_to(repo))]})

    monkeypatch.setattr(policy_signature_gate, "ROOT", repo)
    monkeypatch.setattr(policy_signature_gate, "evidence_root", lambda: repo / "evidence")
    assert policy_signature_gate.main([]) == 1


def test_synthetic_failure_security_unsigned_json_missing_artifact_signature(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)
    _write_json(
        repo / "governance" / "security" / "security_artifact_signature_policy.json",
        {"required_signed_security_json": ["sbom.json"]},
    )
    (sec / "sbom.json").write_text("{}\n", encoding="utf-8")

    monkeypatch.setattr(security_unsigned_json_gate, "ROOT", repo)
    monkeypatch.setattr(
        security_unsigned_json_gate,
        "POLICY",
        repo / "governance" / "security" / "security_artifact_signature_policy.json",
    )
    monkeypatch.setattr(security_unsigned_json_gate, "evidence_root", lambda: repo / "evidence")
    assert security_unsigned_json_gate.main([]) == 1


def test_synthetic_failure_signature_coverage_missing_upload_pair(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    wf = repo / ".github" / "workflows"
    wf.mkdir(parents=True, exist_ok=True)
    _write_json(
        repo / "governance" / "security" / "security_artifact_signature_policy.json",
        {"required_signature_pairs": [{"artifact": "sbom.json", "signature": "sbom.json.sig"}]},
    )
    (wf / "ci.yml").write_text(
        "steps:\n  - uses: actions/upload-artifact@abc\n    with:\n      path: |\n        evidence/security/sbom.json\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(security_artifact_signature_coverage_gate, "ROOT", repo)
    monkeypatch.setattr(
        security_artifact_signature_coverage_gate,
        "POLICY",
        repo / "governance" / "security" / "security_artifact_signature_policy.json",
    )
    monkeypatch.setattr(security_artifact_signature_coverage_gate, "WORKFLOWS", wf)
    monkeypatch.setattr(security_artifact_signature_coverage_gate, "evidence_root", lambda: repo / "evidence")
    assert security_artifact_signature_coverage_gate.main([]) == 1


def test_synthetic_failure_workflow_permissions_write_all(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    wf = repo / ".github" / "workflows"
    wf.mkdir(parents=True, exist_ok=True)
    (wf / "ci.yml").write_text("permissions: write-all\njobs:\n  security-matrix:\n    runs-on: ubuntu-latest\n", encoding="utf-8")

    monkeypatch.setattr(security_workflow_permissions_policy_gate, "ROOT", repo)
    monkeypatch.setattr(security_workflow_permissions_policy_gate, "evidence_root", lambda: repo / "evidence")
    assert security_workflow_permissions_policy_gate.main([]) == 1
