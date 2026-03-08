from __future__ import annotations

import json
from pathlib import Path

from tooling.security import package_metadata_anomaly_gate


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_package_metadata_anomaly_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "package_metadata_anomaly_policy.json"
    snapshot = repo / "governance" / "security" / "metadata" / "dependency_registry_snapshot.json"

    _write_json(
        policy,
        {
            "registry_snapshot_path": "governance/security/metadata/dependency_registry_snapshot.json",
            "disallowed_maintainers": ["evil"],
            "disallowed_email_domains": ["mailinator.com"],
            "expected_package_metadata": {"semgrep": {"maintainers": ["returntocorp"]}},
        },
    )
    _write_json(snapshot, {"packages": {"semgrep": {"maintainers": ["returntocorp"], "emails": ["sec@company.com"]}}})

    monkeypatch.setattr(package_metadata_anomaly_gate, "ROOT", repo)
    monkeypatch.setattr(package_metadata_anomaly_gate, "POLICY", policy)
    monkeypatch.setattr(package_metadata_anomaly_gate, "evidence_root", lambda: repo / "evidence")

    assert package_metadata_anomaly_gate.main([]) == 0


def test_package_metadata_anomaly_gate_fails_on_drift_and_disallowed_domain(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "package_metadata_anomaly_policy.json"
    snapshot = repo / "governance" / "security" / "metadata" / "dependency_registry_snapshot.json"

    _write_json(
        policy,
        {
            "registry_snapshot_path": "governance/security/metadata/dependency_registry_snapshot.json",
            "disallowed_maintainers": ["evil"],
            "disallowed_email_domains": ["mailinator.com"],
            "expected_package_metadata": {"semgrep": {"maintainers": ["returntocorp"]}},
        },
    )
    _write_json(snapshot, {"packages": {"semgrep": {"maintainers": ["evil"], "emails": ["x@mailinator.com"]}}})

    monkeypatch.setattr(package_metadata_anomaly_gate, "ROOT", repo)
    monkeypatch.setattr(package_metadata_anomaly_gate, "POLICY", policy)
    monkeypatch.setattr(package_metadata_anomaly_gate, "evidence_root", lambda: repo / "evidence")

    assert package_metadata_anomaly_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "package_metadata_anomaly_gate.json").read_text(encoding="utf-8"))
    assert "disallowed_maintainer:semgrep:evil" in report["findings"]
    assert "disallowed_email_domain:semgrep:mailinator.com" in report["findings"]
    assert "maintainer_drift:semgrep" in report["findings"]
