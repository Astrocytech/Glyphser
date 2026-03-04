from __future__ import annotations

import json
from pathlib import Path

from tooling.security import report_secret_leak_gate


def test_report_secret_leak_gate_passes_when_clean(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    (sec / "a.json").write_text('{"x":"ok"}\n', encoding="utf-8")
    monkeypatch.setattr(report_secret_leak_gate, "ROOT", repo)
    monkeypatch.setattr(report_secret_leak_gate, "evidence_root", lambda: repo / "evidence")
    assert report_secret_leak_gate.main([]) == 0


def test_report_secret_leak_gate_fails_when_secret_like_content_present(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    (sec / "a.json").write_text('{"password":"hunter2"}\n', encoding="utf-8")
    monkeypatch.setattr(report_secret_leak_gate, "ROOT", repo)
    monkeypatch.setattr(report_secret_leak_gate, "evidence_root", lambda: repo / "evidence")
    assert report_secret_leak_gate.main([]) == 1
    report = json.loads((sec / "report_secret_leak.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
