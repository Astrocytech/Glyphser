from __future__ import annotations

import json
from pathlib import Path

from tooling.security import subprocess_allowlist_report


def test_subprocess_allowlist_report_emits_prefixes_and_callsites(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    security = repo / "tooling" / "security"
    security.mkdir(parents=True)
    evidence = repo / "evidence" / "security"
    evidence.mkdir(parents=True)

    (security / "a.py").write_text("run_checked(['python', '-V'])\n", encoding="utf-8")
    (security / "b.py").write_text("x = 1\n", encoding="utf-8")

    class _Policy:
        _ALLOWED_PREFIXES = [("python",), ("git", "diff")]

    monkeypatch.setattr(subprocess_allowlist_report, "ROOT", repo)
    monkeypatch.setattr(subprocess_allowlist_report, "subprocess_policy", _Policy)
    monkeypatch.setattr(subprocess_allowlist_report, "evidence_root", lambda: repo / "evidence")
    assert subprocess_allowlist_report.main([]) == 0
    report = json.loads((evidence / "subprocess_allowlist_report.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert report["allowed_prefixes"] == [["git", "diff"], ["python"]]
    assert report["callsites"] == ["tooling/security/a.py:1"]
