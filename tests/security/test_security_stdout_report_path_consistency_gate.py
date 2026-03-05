from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_stdout_report_path_consistency_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_security_stdout_report_path_consistency_gate_passes_when_var_matches(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "tooling" / "security"
    _write(
        sec / "alpha_gate.py",
        "def main():\n"
        "    out = None\n"
        "    write_json_report(out, report)\n"
        "    print(f\"Report: {out}\")\n",
    )

    monkeypatch.setattr(security_stdout_report_path_consistency_gate, "ROOT", repo)
    monkeypatch.setattr(security_stdout_report_path_consistency_gate, "SECURITY_TOOLING", sec)
    monkeypatch.setattr(security_stdout_report_path_consistency_gate, "evidence_root", lambda: repo / "evidence")
    assert security_stdout_report_path_consistency_gate.main([]) == 0


def test_security_stdout_report_path_consistency_gate_fails_when_var_differs(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "tooling" / "security"
    _write(
        sec / "beta_gate.py",
        "def main():\n"
        "    out = None\n"
        "    write_json_report(out, report)\n"
        "    print(f\"Report: {other}\")\n",
    )

    monkeypatch.setattr(security_stdout_report_path_consistency_gate, "ROOT", repo)
    monkeypatch.setattr(security_stdout_report_path_consistency_gate, "SECURITY_TOOLING", sec)
    monkeypatch.setattr(security_stdout_report_path_consistency_gate, "evidence_root", lambda: repo / "evidence")
    assert security_stdout_report_path_consistency_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "security_stdout_report_path_consistency_gate.json").read_text(encoding="utf-8"))
    assert "stdout_report_path_mismatch:beta_gate.py" in report["findings"]
