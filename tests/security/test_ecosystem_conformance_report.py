from __future__ import annotations

import json
from pathlib import Path

from tooling.security import ecosystem_conformance_report


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_ecosystem_conformance_report_passes_and_lists_consumer_repos(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    ev = repo / "evidence"
    _write(repo / "governance" / "security" / "security_standards_profile.json", {"consumer_repos": ["repo-a", "repo-b"]})
    _write(repo / "evidence" / "security" / "workflow_pinning_gate.json", {"status": "PASS"})
    _write(repo / "evidence" / "security" / "security_workflow_permissions_policy_gate.json", {"status": "PASS"})
    monkeypatch.setattr(ecosystem_conformance_report, "ROOT", repo)
    monkeypatch.setattr(
        ecosystem_conformance_report,
        "STANDARDS_PROFILE",
        repo / "governance" / "security" / "security_standards_profile.json",
    )
    monkeypatch.setattr(ecosystem_conformance_report, "LOCAL_PINNING_REPORT", repo / "evidence" / "security" / "workflow_pinning_gate.json")
    monkeypatch.setattr(
        ecosystem_conformance_report,
        "LOCAL_PERMISSIONS_REPORT",
        repo / "evidence" / "security" / "security_workflow_permissions_policy_gate.json",
    )
    monkeypatch.setattr(ecosystem_conformance_report, "evidence_root", lambda: ev)
    assert ecosystem_conformance_report.main([]) == 0
    report = json.loads((ev / "security" / "ecosystem_conformance_report.json").read_text(encoding="utf-8"))
    assert report["summary"]["repos_reported"] == 3


def test_ecosystem_conformance_report_fails_when_local_nonconformant(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    ev = repo / "evidence"
    _write(repo / "governance" / "security" / "security_standards_profile.json", {"consumer_repos": []})
    _write(repo / "evidence" / "security" / "workflow_pinning_gate.json", {"status": "FAIL"})
    _write(repo / "evidence" / "security" / "security_workflow_permissions_policy_gate.json", {"status": "PASS"})
    monkeypatch.setattr(ecosystem_conformance_report, "ROOT", repo)
    monkeypatch.setattr(
        ecosystem_conformance_report,
        "STANDARDS_PROFILE",
        repo / "governance" / "security" / "security_standards_profile.json",
    )
    monkeypatch.setattr(ecosystem_conformance_report, "LOCAL_PINNING_REPORT", repo / "evidence" / "security" / "workflow_pinning_gate.json")
    monkeypatch.setattr(
        ecosystem_conformance_report,
        "LOCAL_PERMISSIONS_REPORT",
        repo / "evidence" / "security" / "security_workflow_permissions_policy_gate.json",
    )
    monkeypatch.setattr(ecosystem_conformance_report, "evidence_root", lambda: ev)
    assert ecosystem_conformance_report.main([]) == 1
    report = json.loads((ev / "security" / "ecosystem_conformance_report.json").read_text(encoding="utf-8"))
    assert "local_pinning_nonconformant" in report["findings"]
