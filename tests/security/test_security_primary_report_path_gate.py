from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_primary_report_path_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_security_primary_report_path_gate_passes_for_single_write(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "tooling" / "security"
    _write(
        sec / "alpha_gate.py",
        "from tooling.lib.path_config import evidence_root\n"
        "def main():\n"
        "    out = evidence_root() / \"security\" / \"alpha_gate.json\"\n",
    )

    monkeypatch.setattr(security_primary_report_path_gate, "ROOT", repo)
    monkeypatch.setattr(security_primary_report_path_gate, "SECURITY_TOOLING", sec)
    monkeypatch.setattr(security_primary_report_path_gate, "evidence_root", lambda: repo / "evidence")
    assert security_primary_report_path_gate.main([]) == 0


def test_security_primary_report_path_gate_fails_when_primary_path_reference_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "tooling" / "security"
    _write(
        sec / "beta_gate.py",
        "from tooling.lib.path_config import evidence_root\n"
        "def main():\n"
        "    out = evidence_root() / \"security\" / \"wrong_name.json\"\n",
    )

    monkeypatch.setattr(security_primary_report_path_gate, "ROOT", repo)
    monkeypatch.setattr(security_primary_report_path_gate, "SECURITY_TOOLING", sec)
    monkeypatch.setattr(security_primary_report_path_gate, "evidence_root", lambda: repo / "evidence")
    assert security_primary_report_path_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "security_primary_report_path_gate.json").read_text(encoding="utf-8"))
    assert "missing_primary_report_path_reference:beta_gate.py:beta.json|beta_gate.json" in report["findings"]
