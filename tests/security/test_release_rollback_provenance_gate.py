from __future__ import annotations

import json
from pathlib import Path

from tooling.security import release_rollback_provenance_gate


def _write_status(path: Path, status: str, **extra: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"status": status}
    payload.update(extra)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def _write_available_artifacts(sec: Path) -> None:
    for name in ("sbom.json", "build_provenance.json", "slsa_provenance_v1.json", "security_verification_summary.json"):
        (sec / name).write_text("{}\n", encoding="utf-8")


def test_release_rollback_provenance_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    deploy = repo / "evidence" / "deploy"
    checklist = repo / "governance" / "security" / "EMERGENCY_LOCKDOWN_ROLLBACK_CHECKLIST.md"
    checklist.parent.mkdir(parents=True, exist_ok=True)
    checklist.write_text("7. Execute rollback attestation verification gate.\n", encoding="utf-8")
    policy_digest = "sha256:" + ("a" * 64)
    _write_status(deploy / "latest.json", "PASS", policy_digest=policy_digest)
    _write_status(deploy / "rollback.json", "PASS", policy_digest=policy_digest, previously_attested=True)
    _write_status(sec / "provenance_signature.json", "PASS")
    _write_status(sec / "policy_signature.json", "PASS")
    _write_status(sec / "emergency_lockdown_gate.json", "PASS")
    _write_status(sec / "security_schema_compatibility_policy_gate.json", "PASS")
    _write_status(sec / "conformance_security_coupling.json", "PASS")
    _write_available_artifacts(sec)

    monkeypatch.setattr(release_rollback_provenance_gate, "ROOT", repo)
    monkeypatch.setattr(release_rollback_provenance_gate, "evidence_root", lambda: repo / "evidence")
    assert release_rollback_provenance_gate.main([]) == 0


def test_release_rollback_provenance_gate_fails_when_any_dependency_not_pass(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    deploy = repo / "evidence" / "deploy"
    checklist = repo / "governance" / "security" / "EMERGENCY_LOCKDOWN_ROLLBACK_CHECKLIST.md"
    checklist.parent.mkdir(parents=True, exist_ok=True)
    checklist.write_text("7. Execute rollback attestation verification gate.\n", encoding="utf-8")
    policy_digest = "sha256:" + ("b" * 64)
    _write_status(deploy / "latest.json", "PASS", policy_digest=policy_digest)
    _write_status(deploy / "rollback.json", "FAIL", policy_digest=policy_digest, previously_attested=True)
    _write_status(sec / "provenance_signature.json", "PASS")
    _write_status(sec / "policy_signature.json", "PASS")
    _write_status(sec / "emergency_lockdown_gate.json", "PASS")
    _write_status(sec / "security_schema_compatibility_policy_gate.json", "PASS")
    _write_status(sec / "conformance_security_coupling.json", "PASS")
    _write_available_artifacts(sec)

    monkeypatch.setattr(release_rollback_provenance_gate, "ROOT", repo)
    monkeypatch.setattr(release_rollback_provenance_gate, "evidence_root", lambda: repo / "evidence")
    assert release_rollback_provenance_gate.main([]) == 1


def test_release_rollback_provenance_gate_fails_when_checklist_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    deploy = repo / "evidence" / "deploy"
    policy_digest = "sha256:" + ("c" * 64)
    _write_status(deploy / "latest.json", "PASS", policy_digest=policy_digest)
    _write_status(deploy / "rollback.json", "PASS", policy_digest=policy_digest, previously_attested=True)
    _write_status(sec / "provenance_signature.json", "PASS")
    _write_status(sec / "policy_signature.json", "PASS")
    _write_status(sec / "emergency_lockdown_gate.json", "PASS")
    _write_status(sec / "security_schema_compatibility_policy_gate.json", "PASS")
    _write_status(sec / "conformance_security_coupling.json", "PASS")
    _write_available_artifacts(sec)
    monkeypatch.setattr(release_rollback_provenance_gate, "ROOT", repo)
    monkeypatch.setattr(release_rollback_provenance_gate, "evidence_root", lambda: repo / "evidence")
    assert release_rollback_provenance_gate.main([]) == 1


def test_release_rollback_provenance_gate_fails_when_compatibility_not_pass(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    deploy = repo / "evidence" / "deploy"
    checklist = repo / "governance" / "security" / "EMERGENCY_LOCKDOWN_ROLLBACK_CHECKLIST.md"
    checklist.parent.mkdir(parents=True, exist_ok=True)
    checklist.write_text("7. Execute rollback attestation verification gate.\n", encoding="utf-8")
    policy_digest = "sha256:" + ("d" * 64)
    _write_status(deploy / "latest.json", "PASS", policy_digest=policy_digest)
    _write_status(deploy / "rollback.json", "PASS", policy_digest=policy_digest, previously_attested=True)
    _write_status(sec / "provenance_signature.json", "PASS")
    _write_status(sec / "policy_signature.json", "PASS")
    _write_status(sec / "emergency_lockdown_gate.json", "PASS")
    _write_status(sec / "security_schema_compatibility_policy_gate.json", "FAIL")
    _write_status(sec / "conformance_security_coupling.json", "PASS")
    _write_available_artifacts(sec)
    monkeypatch.setattr(release_rollback_provenance_gate, "ROOT", repo)
    monkeypatch.setattr(release_rollback_provenance_gate, "evidence_root", lambda: repo / "evidence")
    assert release_rollback_provenance_gate.main([]) == 1


def test_release_rollback_provenance_gate_fails_when_policy_digest_mismatch_or_not_attested(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    deploy = repo / "evidence" / "deploy"
    checklist = repo / "governance" / "security" / "EMERGENCY_LOCKDOWN_ROLLBACK_CHECKLIST.md"
    checklist.parent.mkdir(parents=True, exist_ok=True)
    checklist.write_text("7. Execute rollback attestation verification gate.\n", encoding="utf-8")
    _write_status(deploy / "latest.json", "PASS", policy_digest="sha256:" + ("e" * 64))
    _write_status(deploy / "rollback.json", "PASS", policy_digest="sha256:" + ("f" * 64), previously_attested=False)
    _write_status(sec / "provenance_signature.json", "PASS")
    _write_status(sec / "policy_signature.json", "PASS")
    _write_status(sec / "emergency_lockdown_gate.json", "PASS")
    _write_status(sec / "security_schema_compatibility_policy_gate.json", "PASS")
    _write_status(sec / "conformance_security_coupling.json", "PASS")
    _write_available_artifacts(sec)
    monkeypatch.setattr(release_rollback_provenance_gate, "ROOT", repo)
    monkeypatch.setattr(release_rollback_provenance_gate, "evidence_root", lambda: repo / "evidence")
    assert release_rollback_provenance_gate.main([]) == 1
    payload = json.loads((sec / "release_rollback_provenance_gate.json").read_text(encoding="utf-8"))
    assert "rollback_policy_digest_mismatch" in payload["findings"]
    assert "rollback_not_previously_attested" in payload["findings"]
