from __future__ import annotations

import json
from pathlib import Path

from tooling.security import bandit_baseline_gate


def test_bandit_baseline_gate_passes_with_approved_finding(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "governance" / "security").mkdir(parents=True)
    (repo / "governance" / "security" / "bandit_baseline_policy.json").write_text(
        json.dumps(
            {
                "max_severity_counts": {"LOW": 1, "MEDIUM": 0, "HIGH": 0},
                "allowed_findings": ["B105:tooling/security/x.py:10"],
                "enforce_approved_findings_only": True,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (repo / "bandit.json").write_text(
        json.dumps(
            {
                "results": [
                    {
                        "test_id": "B105",
                        "filename": "tooling/security/x.py",
                        "line_number": 10,
                        "issue_severity": "LOW",
                    }
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(bandit_baseline_gate, "ROOT", repo)
    monkeypatch.setattr(
        bandit_baseline_gate, "POLICY", repo / "governance" / "security" / "bandit_baseline_policy.json"
    )
    monkeypatch.setattr(bandit_baseline_gate, "evidence_root", lambda: repo / "evidence")
    assert bandit_baseline_gate.main([]) == 0


def test_bandit_baseline_gate_fails_on_unapproved_or_excess_findings(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "governance" / "security").mkdir(parents=True)
    (repo / "governance" / "security" / "bandit_baseline_policy.json").write_text(
        json.dumps(
            {
                "max_severity_counts": {"LOW": 0, "MEDIUM": 0, "HIGH": 0},
                "allowed_findings": [],
                "enforce_approved_findings_only": True,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (repo / "bandit.json").write_text(
        json.dumps(
            {
                "results": [
                    {
                        "test_id": "B105",
                        "filename": "tooling/security/y.py",
                        "line_number": 20,
                        "issue_severity": "LOW",
                    }
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(bandit_baseline_gate, "ROOT", repo)
    monkeypatch.setattr(
        bandit_baseline_gate, "POLICY", repo / "governance" / "security" / "bandit_baseline_policy.json"
    )
    monkeypatch.setattr(bandit_baseline_gate, "evidence_root", lambda: repo / "evidence")
    assert bandit_baseline_gate.main([]) == 1
