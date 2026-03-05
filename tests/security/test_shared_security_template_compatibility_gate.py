from __future__ import annotations

import json
from pathlib import Path

from tooling.security import shared_security_template_compatibility_gate


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_shared_security_template_compatibility_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    ev = repo / "evidence"
    _write_text(repo / ".github" / "workflows" / "security-maintenance.yml", "python tooling/security/security_super_gate.py --strict-key --strict-prereqs\n")
    _write_text(repo / "governance" / "security" / "workflow_policy_coverage.json", '{"schema_version": 1, "workflows": []}\n')
    _write_json(
        repo / "governance" / "security" / "shared_security_template_compatibility.json",
        {
            "templates": [
                {
                    "path": ".github/workflows/security-maintenance.yml",
                    "required_markers": ["security_super_gate.py --strict-key --strict-prereqs"],
                },
                {"path": "governance/security/workflow_policy_coverage.json", "required_markers": ['"workflows"']},
            ]
        },
    )
    monkeypatch.setattr(shared_security_template_compatibility_gate, "ROOT", repo)
    monkeypatch.setattr(
        shared_security_template_compatibility_gate,
        "POLICY",
        repo / "governance" / "security" / "shared_security_template_compatibility.json",
    )
    monkeypatch.setattr(shared_security_template_compatibility_gate, "evidence_root", lambda: ev)
    assert shared_security_template_compatibility_gate.main([]) == 0


def test_shared_security_template_compatibility_gate_fails_when_marker_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    ev = repo / "evidence"
    _write_text(repo / ".github" / "workflows" / "security-maintenance.yml", "jobs:\n")
    _write_json(
        repo / "governance" / "security" / "shared_security_template_compatibility.json",
        {
            "templates": [
                {
                    "path": ".github/workflows/security-maintenance.yml",
                    "required_markers": ["security_super_gate.py --strict-key --strict-prereqs"],
                }
            ]
        },
    )
    monkeypatch.setattr(shared_security_template_compatibility_gate, "ROOT", repo)
    monkeypatch.setattr(
        shared_security_template_compatibility_gate,
        "POLICY",
        repo / "governance" / "security" / "shared_security_template_compatibility.json",
    )
    monkeypatch.setattr(shared_security_template_compatibility_gate, "evidence_root", lambda: ev)
    assert shared_security_template_compatibility_gate.main([]) == 1
    report = json.loads((ev / "security" / "shared_security_template_compatibility_gate.json").read_text(encoding="utf-8"))
    assert any(str(item).startswith("missing_marker:.github/workflows/security-maintenance.yml:") for item in report["findings"])
