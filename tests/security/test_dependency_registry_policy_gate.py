from __future__ import annotations

import json
from pathlib import Path

from tooling.security import dependency_registry_policy_gate


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_dependency_registry_policy_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "governance" / "security" / "metadata").mkdir(parents=True)
    (repo / "requirements.lock").write_text("safepkg==1.2.3\n", encoding="utf-8")
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
        {"packages": {"safepkg": {"maintainers": ["safe-owner"], "yanked_versions": []}}},
    )

    monkeypatch.setattr(dependency_registry_policy_gate, "ROOT", repo)
    monkeypatch.setattr(
        dependency_registry_policy_gate,
        "POLICY_PATH",
        repo / "governance" / "security" / "dependency_registry_policy.json",
    )
    monkeypatch.setattr(dependency_registry_policy_gate, "LOCK_PATH", repo / "requirements.lock")
    monkeypatch.setattr(dependency_registry_policy_gate, "evidence_root", lambda: repo / "evidence")
    assert dependency_registry_policy_gate.main([]) == 0
    report = json.loads((repo / "evidence" / "security" / "dependency_registry_policy_gate.json").read_text("utf-8"))
    assert report["status"] == "PASS"


def test_dependency_registry_policy_gate_fails_for_forbidden_maintainer_and_yanked(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    (repo / "governance" / "security" / "metadata").mkdir(parents=True)
    (repo / "requirements.lock").write_text("badpkg==9.9.9\n", encoding="utf-8")
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
        {"packages": {"badpkg": {"maintainers": ["bad-owner"], "yanked_versions": ["9.9.9"]}}},
    )

    monkeypatch.setattr(dependency_registry_policy_gate, "ROOT", repo)
    monkeypatch.setattr(
        dependency_registry_policy_gate,
        "POLICY_PATH",
        repo / "governance" / "security" / "dependency_registry_policy.json",
    )
    monkeypatch.setattr(dependency_registry_policy_gate, "LOCK_PATH", repo / "requirements.lock")
    monkeypatch.setattr(dependency_registry_policy_gate, "evidence_root", lambda: repo / "evidence")
    assert dependency_registry_policy_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "dependency_registry_policy_gate.json").read_text("utf-8"))
    assert report["status"] == "FAIL"
    assert "forbidden_maintainer:badpkg:bad-owner" in report["findings"]
    assert "yanked_version:badpkg:9.9.9" in report["findings"]
