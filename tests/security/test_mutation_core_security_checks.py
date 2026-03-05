from __future__ import annotations

import json
from pathlib import Path

from tooling.security import (
    dependency_registry_policy_gate,
    lockfile_change_provenance_gate,
    provenance_signature_gate,
)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_mutation_dependency_registry_forbidden_maintainer_check(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True, exist_ok=True)
    (repo / "requirements.lock").write_text("badpkg==1.0.0\n", encoding="utf-8")
    _write_json(
        repo / "governance" / "security" / "dependency_registry_policy.json",
        {
            "registry_snapshot_path": "governance/security/metadata/dependency_registry_snapshot.json",
            "forbidden_maintainers": ["bad-owner"],
            "fail_on_missing_snapshot": True,
            "fail_on_missing_package_metadata": True,
        },
    )
    _write_json(
        repo / "governance" / "security" / "metadata" / "dependency_registry_snapshot.json",
        {"packages": {"badpkg": {"maintainers": ["bad-owner"], "yanked_versions": []}}},
    )

    monkeypatch.setattr(dependency_registry_policy_gate, "ROOT", repo)
    monkeypatch.setattr(
        dependency_registry_policy_gate,
        "POLICY_PATH",
        repo / "governance" / "security" / "dependency_registry_policy.json",
    )
    monkeypatch.setattr(dependency_registry_policy_gate, "LOCK_PATH", repo / "requirements.lock")
    monkeypatch.setattr(dependency_registry_policy_gate, "evidence_root", lambda: repo / "evidence")
    baseline = dependency_registry_policy_gate.main([])
    assert baseline == 1

    # Mutant: forbidden maintainers list emptied.
    _write_json(
        repo / "governance" / "security" / "dependency_registry_policy.json",
        {
            "registry_snapshot_path": "governance/security/metadata/dependency_registry_snapshot.json",
            "forbidden_maintainers": [],
            "fail_on_missing_snapshot": True,
            "fail_on_missing_package_metadata": True,
        },
    )
    mutant = dependency_registry_policy_gate.main([])
    assert mutant == 0
    assert mutant != baseline


def test_mutation_lockfile_change_detection_toggle(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True, exist_ok=True)
    (repo / "requirements.lock").write_text("pytest==8.3.3\n", encoding="utf-8")
    monkeypatch.setattr(lockfile_change_provenance_gate, "ROOT", repo)
    monkeypatch.setattr(lockfile_change_provenance_gate, "LOCKFILE_PATH", repo / "requirements.lock")
    monkeypatch.setattr(
        lockfile_change_provenance_gate,
        "APPROVAL_FILE",
        repo / "governance" / "security" / "lockfile_change_approval.json",
    )
    monkeypatch.setattr(lockfile_change_provenance_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(lockfile_change_provenance_gate, "_changed_files", lambda: ["requirements.lock"])

    monkeypatch.setattr(lockfile_change_provenance_gate, "_lockfile_changed", lambda: True)
    baseline = lockfile_change_provenance_gate.main([])
    assert baseline == 1

    # Mutant: core change detector toggled off.
    monkeypatch.setattr(lockfile_change_provenance_gate, "_lockfile_changed", lambda: False)
    mutant = lockfile_change_provenance_gate.main([])
    assert mutant == 0
    assert mutant != baseline


def test_mutation_provenance_signature_pair_verification(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)
    (sec / "sbom.json").write_text("{}\n", encoding="utf-8")
    (sec / "build_provenance.json").write_text("{}\n", encoding="utf-8")
    (sec / "slsa_provenance_v1.json").write_text("{}\n", encoding="utf-8")
    # Intentionally omit signatures to force baseline failure.

    monkeypatch.setattr(provenance_signature_gate, "ROOT", repo)
    monkeypatch.setattr(provenance_signature_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(provenance_signature_gate, "current_key", lambda strict=False: b"k")
    baseline = provenance_signature_gate.main([])
    assert baseline == 1

    # Mutant: pair verification forcibly returns success.
    monkeypatch.setattr(provenance_signature_gate, "_verify_pair", lambda path, sig, strict_key: (True, "ok"))
    mutant = provenance_signature_gate.main([])
    assert mutant == 0
    assert mutant != baseline
