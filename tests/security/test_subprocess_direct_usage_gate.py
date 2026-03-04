from __future__ import annotations

import json
from pathlib import Path

from tooling.security import subprocess_direct_usage_gate


def test_subprocess_direct_usage_gate_passes_without_direct_usage(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    security = repo / "tooling" / "security"
    security.mkdir(parents=True)
    evidence = repo / "evidence" / "security"
    evidence.mkdir(parents=True)
    (security / "ok.py").write_text("x = 1\n", encoding="utf-8")
    (security / "subprocess_policy.py").write_text("import subprocess\n", encoding="utf-8")

    monkeypatch.setattr(subprocess_direct_usage_gate, "ROOT", repo)
    monkeypatch.setattr(subprocess_direct_usage_gate, "evidence_root", lambda: repo / "evidence")
    assert subprocess_direct_usage_gate.main([]) == 0


def test_subprocess_direct_usage_gate_fails_on_direct_usage(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    security = repo / "tooling" / "security"
    security.mkdir(parents=True)
    evidence = repo / "evidence" / "security"
    evidence.mkdir(parents=True)
    (security / "bad.py").write_text("import subprocess\nsubprocess.run(['x'])\n", encoding="utf-8")

    monkeypatch.setattr(subprocess_direct_usage_gate, "ROOT", repo)
    monkeypatch.setattr(subprocess_direct_usage_gate, "evidence_root", lambda: repo / "evidence")
    assert subprocess_direct_usage_gate.main([]) == 1
    report = json.loads((evidence / "subprocess_direct_usage_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(item.startswith("direct_subprocess_import:") for item in report["findings"])
