from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_schema_migration_tracker


def test_security_schema_migration_tracker_reports_migrated_vs_legacy(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    sec = repo / "tooling" / "security"
    sec.mkdir(parents=True)
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True)

    (sec / "a_gate.py").write_text("write_json_report(out, report)\n", encoding="utf-8")
    (sec / "b_gate.py").write_text("out.write_text('x')\n", encoding="utf-8")

    monkeypatch.setattr(security_schema_migration_tracker, "ROOT", repo)
    monkeypatch.setattr(security_schema_migration_tracker, "evidence_root", lambda: repo / "evidence")
    assert security_schema_migration_tracker.main([]) == 0
    report = json.loads((ev / "security_schema_migration_tracker.json").read_text(encoding="utf-8"))
    assert report["summary"]["total_gate_scripts"] == 2
    assert report["summary"]["migrated_count"] == 1
    assert report["summary"]["legacy_count"] == 1
