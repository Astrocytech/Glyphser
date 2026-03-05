from __future__ import annotations

import json
from pathlib import Path

from tooling.security import temp_directory_policy_gate


def test_temp_directory_policy_gate_fails_on_forbidden_patterns(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "tooling" / "security"
    sec.mkdir(parents=True, exist_ok=True)
    (sec / "bad.py").write_text(
        "import tempfile\nx = tempfile.mktemp(prefix='x')\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(temp_directory_policy_gate, "ROOT", repo)
    monkeypatch.setattr(temp_directory_policy_gate, "SCAN_DIRS", [repo / "tooling" / "security"])
    monkeypatch.setattr(temp_directory_policy_gate, "evidence_root", lambda: repo / "evidence")
    assert temp_directory_policy_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "temp_directory_policy_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(str(item).startswith("forbidden_tempfile_mktemp:") for item in report["findings"])


def test_temp_directory_policy_gate_passes_for_temporary_directory_context(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "tooling" / "security"
    sec.mkdir(parents=True, exist_ok=True)
    (sec / "good.py").write_text(
        "import tempfile\n\nwith tempfile.TemporaryDirectory(prefix='x') as td:\n    print(td)\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(temp_directory_policy_gate, "ROOT", repo)
    monkeypatch.setattr(temp_directory_policy_gate, "SCAN_DIRS", [repo / "tooling" / "security"])
    monkeypatch.setattr(temp_directory_policy_gate, "evidence_root", lambda: repo / "evidence")
    assert temp_directory_policy_gate.main([]) == 0
