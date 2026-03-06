from __future__ import annotations

import json
from pathlib import Path

from tooling.security import workflow_artifact_retention_gate


def _write_policy(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        (
            '{\n'
            '  "workflow_classes": {\n'
            '    "ci.yml": "ci",\n'
            '    "security-maintenance.yml": "security_maintenance",\n'
            '    "security-super-extended.yml": "security_maintenance",\n'
            '    "release.yml": "release"\n'
            "  },\n"
            '  "retention_days_by_class": {\n'
            '    "ci": 14,\n'
            '    "security_maintenance": 30,\n'
            '    "release": 180\n'
            "  }\n"
            "}\n"
        ),
        encoding="utf-8",
    )


def test_workflow_artifact_retention_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    wf = repo / ".github" / "workflows"
    wf.mkdir(parents=True)
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True)
    (wf / "ci.yml").write_text("uses: actions/upload-artifact@x\nretention-days: 14\n", encoding="utf-8")
    (wf / "security-maintenance.yml").write_text(
        "uses: actions/upload-artifact@x\nretention-days: 30\n", encoding="utf-8"
    )
    (wf / "security-super-extended.yml").write_text(
        "uses: actions/upload-artifact@x\nretention-days: 30\n", encoding="utf-8"
    )
    (wf / "release.yml").write_text("uses: actions/upload-artifact@x\nretention-days: 180\n", encoding="utf-8")
    _write_policy(repo / "governance" / "security" / "workflow_artifact_retention_policy.json")
    monkeypatch.setattr(workflow_artifact_retention_gate, "ROOT", repo)
    monkeypatch.setattr(
        workflow_artifact_retention_gate,
        "POLICY",
        repo / "governance" / "security" / "workflow_artifact_retention_policy.json",
    )
    monkeypatch.setattr(workflow_artifact_retention_gate, "evidence_root", lambda: repo / "evidence")
    assert workflow_artifact_retention_gate.main([]) == 0


def test_workflow_artifact_retention_gate_fails_when_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    wf = repo / ".github" / "workflows"
    wf.mkdir(parents=True)
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True)
    (wf / "ci.yml").write_text("uses: actions/upload-artifact@x\n", encoding="utf-8")
    (wf / "security-maintenance.yml").write_text("uses: actions/upload-artifact@x\nretention-days: 30\n", encoding="utf-8")
    (wf / "security-super-extended.yml").write_text("uses: actions/upload-artifact@x\nretention-days: 30\n", encoding="utf-8")
    (wf / "release.yml").write_text("uses: actions/upload-artifact@x\nretention-days: 180\n", encoding="utf-8")
    _write_policy(repo / "governance" / "security" / "workflow_artifact_retention_policy.json")
    monkeypatch.setattr(workflow_artifact_retention_gate, "ROOT", repo)
    monkeypatch.setattr(
        workflow_artifact_retention_gate,
        "POLICY",
        repo / "governance" / "security" / "workflow_artifact_retention_policy.json",
    )
    monkeypatch.setattr(workflow_artifact_retention_gate, "evidence_root", lambda: repo / "evidence")
    assert workflow_artifact_retention_gate.main([]) == 1
    report = json.loads((ev / "workflow_artifact_retention_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(item.startswith("missing_retention_policy:ci.yml:retention-days: 14:class=ci") for item in report["findings"])


def test_workflow_artifact_retention_gate_fails_when_policy_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    wf = repo / ".github" / "workflows"
    wf.mkdir(parents=True)
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True)
    (wf / "ci.yml").write_text("uses: actions/upload-artifact@x\nretention-days: 14\n", encoding="utf-8")
    monkeypatch.setattr(workflow_artifact_retention_gate, "ROOT", repo)
    monkeypatch.setattr(
        workflow_artifact_retention_gate,
        "POLICY",
        repo / "governance" / "security" / "workflow_artifact_retention_policy.json",
    )
    monkeypatch.setattr(workflow_artifact_retention_gate, "evidence_root", lambda: repo / "evidence")
    assert workflow_artifact_retention_gate.main([]) == 1
    report = json.loads((ev / "workflow_artifact_retention_gate.json").read_text(encoding="utf-8"))
    assert "missing_retention_policy" in report["findings"]
