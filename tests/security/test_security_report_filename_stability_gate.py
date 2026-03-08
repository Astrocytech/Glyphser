from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_report_filename_stability_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_security_report_filename_stability_gate_passes_when_baseline_matches(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "tooling" / "security"
    _write(sec / "alpha_gate.py", 'out = evidence_root() / "security" / "alpha.json"\n')
    baseline = repo / "governance" / "security" / "security_report_filename_baseline.json"
    _write_json(baseline, {"report_filenames": ["alpha.json"]})

    monkeypatch.setattr(security_report_filename_stability_gate, "ROOT", repo)
    monkeypatch.setattr(security_report_filename_stability_gate, "SECURITY_TOOLING", sec)
    monkeypatch.setattr(security_report_filename_stability_gate, "BASELINE", baseline)
    monkeypatch.setattr(security_report_filename_stability_gate, "evidence_root", lambda: repo / "evidence")
    assert security_report_filename_stability_gate.main([]) == 0


def test_security_report_filename_stability_gate_fails_when_added_or_removed(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "tooling" / "security"
    _write(sec / "alpha_gate.py", 'out = evidence_root() / "security" / "alpha.json"\n')
    baseline = repo / "governance" / "security" / "security_report_filename_baseline.json"
    _write_json(baseline, {"report_filenames": ["beta.json"]})

    monkeypatch.setattr(security_report_filename_stability_gate, "ROOT", repo)
    monkeypatch.setattr(security_report_filename_stability_gate, "SECURITY_TOOLING", sec)
    monkeypatch.setattr(security_report_filename_stability_gate, "BASELINE", baseline)
    monkeypatch.setattr(security_report_filename_stability_gate, "evidence_root", lambda: repo / "evidence")
    assert security_report_filename_stability_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "security_report_filename_stability_gate.json").read_text(encoding="utf-8"))
    assert "report_filenames_added:1" in report["findings"]
    assert "report_filenames_removed:1" in report["findings"]
