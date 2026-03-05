from __future__ import annotations

import json
from pathlib import Path

from tooling.security import deploy_artifact_drift_gate


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_deploy_artifact_drift_gate_passes_when_drift_within_policy(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "deploy_artifact_drift_policy.json"
    _write(
        policy,
        {
            "deploy_manifest_path": "evidence/deploy/latest.json",
            "build_provenance_path": "evidence/security/build_provenance.json",
            "max_allowed_drift": 0,
        },
    )
    _write(repo / "evidence" / "security" / "build_provenance.json", {"artifact_digests": ["sha256:a"]})
    _write(repo / "evidence" / "deploy" / "latest.json", {"artifact_digests": ["sha256:a"]})
    monkeypatch.setattr(deploy_artifact_drift_gate, "ROOT", repo)
    monkeypatch.setattr(deploy_artifact_drift_gate, "POLICY", policy)
    monkeypatch.setattr(deploy_artifact_drift_gate, "evidence_root", lambda: repo / "evidence")
    assert deploy_artifact_drift_gate.main([]) == 0


def test_deploy_artifact_drift_gate_fails_when_drift_exceeds_policy(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "deploy_artifact_drift_policy.json"
    _write(
        policy,
        {
            "deploy_manifest_path": "evidence/deploy/latest.json",
            "build_provenance_path": "evidence/security/build_provenance.json",
            "max_allowed_drift": 0,
        },
    )
    _write(repo / "evidence" / "security" / "build_provenance.json", {"artifact_digests": ["sha256:a"]})
    _write(repo / "evidence" / "deploy" / "latest.json", {"artifact_digests": ["sha256:b"]})
    monkeypatch.setattr(deploy_artifact_drift_gate, "ROOT", repo)
    monkeypatch.setattr(deploy_artifact_drift_gate, "POLICY", policy)
    monkeypatch.setattr(deploy_artifact_drift_gate, "evidence_root", lambda: repo / "evidence")
    assert deploy_artifact_drift_gate.main([]) == 1
