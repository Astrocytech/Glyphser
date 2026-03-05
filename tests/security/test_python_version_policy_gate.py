from __future__ import annotations

import json
from pathlib import Path

from tooling.security import python_version_policy_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict) -> None:
    _write(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def test_python_version_policy_gate_passes_for_approved_versions(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write(
        repo / ".github" / "workflows" / "ci.yml",
        "jobs:\n  test:\n    steps:\n      - uses: actions/setup-python@x\n        with:\n          python-version: ['3.11', '3.12']\n",
    )
    _write_json(
        repo / "governance" / "security" / "python_version_policy.json",
        {
            "approved_python_minors": ["3.11", "3.12"],
            "warn_before_eol_days": 30,
            "minor_eol_dates_utc": {"3.11": "2029-01-01", "3.12": "2030-01-01"},
        },
    )

    monkeypatch.setattr(python_version_policy_gate, "ROOT", repo)
    monkeypatch.setattr(python_version_policy_gate, "POLICY", repo / "governance" / "security" / "python_version_policy.json")
    monkeypatch.setattr(python_version_policy_gate, "WORKFLOWS_DIR", repo / ".github" / "workflows")
    monkeypatch.setattr(python_version_policy_gate, "evidence_root", lambda: repo / "evidence")

    assert python_version_policy_gate.main([]) == 0
    report = json.loads((repo / "evidence" / "security" / "python_version_policy_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"


def test_python_version_policy_gate_fails_for_unapproved_minor(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write(
        repo / ".github" / "workflows" / "ci.yml",
        "jobs:\n  test:\n    steps:\n      - uses: actions/setup-python@x\n        with:\n          python-version: ['3.13']\n",
    )
    _write_json(
        repo / "governance" / "security" / "python_version_policy.json",
        {
            "approved_python_minors": ["3.11", "3.12"],
            "warn_before_eol_days": 365,
            "minor_eol_dates_utc": {"3.11": "2029-01-01", "3.12": "2030-01-01"},
        },
    )

    monkeypatch.setattr(python_version_policy_gate, "ROOT", repo)
    monkeypatch.setattr(python_version_policy_gate, "POLICY", repo / "governance" / "security" / "python_version_policy.json")
    monkeypatch.setattr(python_version_policy_gate, "WORKFLOWS_DIR", repo / ".github" / "workflows")
    monkeypatch.setattr(python_version_policy_gate, "evidence_root", lambda: repo / "evidence")

    assert python_version_policy_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "python_version_policy_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(item.startswith("unapproved_python_minor:3.13") for item in report["findings"])


def test_python_version_policy_gate_warns_before_eol(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write(
        repo / ".github" / "workflows" / "ci.yml",
        "jobs:\n  test:\n    steps:\n      - uses: actions/setup-python@x\n        with:\n          python-version: ['3.11']\n",
    )
    _write_json(
        repo / "governance" / "security" / "python_version_policy.json",
        {
            "approved_python_minors": ["3.11"],
            "warn_before_eol_days": 99999,
            "minor_eol_dates_utc": {"3.11": "2099-01-01"},
        },
    )

    monkeypatch.setattr(python_version_policy_gate, "ROOT", repo)
    monkeypatch.setattr(python_version_policy_gate, "POLICY", repo / "governance" / "security" / "python_version_policy.json")
    monkeypatch.setattr(python_version_policy_gate, "WORKFLOWS_DIR", repo / ".github" / "workflows")
    monkeypatch.setattr(python_version_policy_gate, "evidence_root", lambda: repo / "evidence")

    assert python_version_policy_gate.main([]) == 0
    report = json.loads((repo / "evidence" / "security" / "python_version_policy_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "WARN"
    assert any(item.startswith("python_minor_eol_warning:3.11") for item in report["findings"])
