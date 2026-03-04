from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_scan_ordering_gate


def test_security_scan_ordering_gate_passes_when_scans_sorted(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "tooling" / "security"
    sec.mkdir(parents=True)
    (sec / "ok_gate.py").write_text(
        "from pathlib import Path\n"
        "def run(base: Path) -> int:\n"
        "    n = 0\n"
        "    for p in sorted(base.rglob('*')):\n"
        "        n += 1\n"
        "    return n\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(security_scan_ordering_gate, "ROOT", repo)
    monkeypatch.setattr(security_scan_ordering_gate, "evidence_root", lambda: repo / "evidence")
    assert security_scan_ordering_gate.main([]) == 0


def test_security_scan_ordering_gate_fails_on_unsorted_scan(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "tooling" / "security"
    sec.mkdir(parents=True)
    (sec / "bad_gate.py").write_text(
        "from pathlib import Path\n"
        "def run(base: Path) -> int:\n"
        "    n = 0\n"
        "    for p in base.rglob('*'):\n"
        "        n += 1\n"
        "    return n\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(security_scan_ordering_gate, "ROOT", repo)
    monkeypatch.setattr(security_scan_ordering_gate, "evidence_root", lambda: repo / "evidence")
    assert security_scan_ordering_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "security_scan_ordering_gate.json").read_text())
    assert report["status"] == "FAIL"
    assert any(str(item).startswith("unsorted_scan_iteration:") for item in report["findings"])
