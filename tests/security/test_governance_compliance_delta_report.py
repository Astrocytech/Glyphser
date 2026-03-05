from __future__ import annotations

import json
from pathlib import Path

from tooling.security import governance_compliance_delta_report


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_governance_compliance_delta_report_passes_when_controls_match(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "governance" / "security").mkdir(parents=True, exist_ok=True)
    (repo / "tooling" / "security").mkdir(parents=True, exist_ok=True)
    (repo / "evidence" / "security").mkdir(parents=True, exist_ok=True)

    (repo / "tooling" / "security" / "security_super_gate_manifest.json").write_text("{}\n", encoding="utf-8")
    _write(
        repo / "governance" / "security" / "governance_compliance_baseline.json",
        {
            "schema_version": 1,
            "controls": [
                {
                    "id": "CTRL-MANIFEST",
                    "type": "file_exists",
                    "path": "tooling/security/security_super_gate_manifest.json",
                }
            ],
        },
    )

    monkeypatch.setattr(governance_compliance_delta_report, "ROOT", repo)
    monkeypatch.setattr(governance_compliance_delta_report, "BASELINE_POLICY", repo / "governance/security/governance_compliance_baseline.json")
    monkeypatch.setattr(governance_compliance_delta_report, "evidence_root", lambda: repo / "evidence")
    monkeypatch.delenv("GLYPHSER_COMPLIANCE_BASELINE_PATH", raising=False)

    assert governance_compliance_delta_report.main([]) == 0
    report = json.loads((repo / "evidence" / "security" / "governance_compliance_delta_report.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert report["summary"]["delta_controls"] == 0


def test_governance_compliance_delta_report_warns_on_delta(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "governance" / "security").mkdir(parents=True, exist_ok=True)
    (repo / "evidence" / "security").mkdir(parents=True, exist_ok=True)

    _write(
        repo / "governance" / "security" / "governance_compliance_baseline.json",
        {
            "schema_version": 1,
            "controls": [
                {
                    "id": "CTRL-MISSING",
                    "type": "file_exists",
                    "path": "tooling/security/does_not_exist.txt",
                }
            ],
        },
    )

    monkeypatch.setattr(governance_compliance_delta_report, "ROOT", repo)
    monkeypatch.setattr(governance_compliance_delta_report, "BASELINE_POLICY", repo / "governance/security/governance_compliance_baseline.json")
    monkeypatch.setattr(governance_compliance_delta_report, "evidence_root", lambda: repo / "evidence")
    monkeypatch.delenv("GLYPHSER_COMPLIANCE_BASELINE_PATH", raising=False)

    assert governance_compliance_delta_report.main([]) == 0
    report = json.loads((repo / "evidence" / "security" / "governance_compliance_delta_report.json").read_text(encoding="utf-8"))
    assert report["status"] == "WARN"
    assert report["summary"]["delta_controls"] == 1
    assert report["delta"][0]["id"] == "CTRL-MISSING"


def test_governance_compliance_delta_report_fails_for_missing_baseline(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "evidence" / "security").mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(governance_compliance_delta_report, "ROOT", repo)
    monkeypatch.setattr(governance_compliance_delta_report, "BASELINE_POLICY", repo / "governance/security/missing.json")
    monkeypatch.setattr(governance_compliance_delta_report, "evidence_root", lambda: repo / "evidence")
    monkeypatch.delenv("GLYPHSER_COMPLIANCE_BASELINE_PATH", raising=False)

    assert governance_compliance_delta_report.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "governance_compliance_delta_report.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(str(item).startswith("missing_baseline:") for item in report["findings"])
