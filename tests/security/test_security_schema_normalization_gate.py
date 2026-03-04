from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_schema_normalization_gate


def test_security_schema_normalization_gate_reports_normalization_metrics(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    (sec / "a.json").write_text(
        json.dumps({"status": "PASS", "findings": [], "summary": {}, "metadata": {}, "schema_version": 1}) + "\n",
        encoding="utf-8",
    )
    (sec / "b.json").write_text(json.dumps({"status": "PASS"}) + "\n", encoding="utf-8")
    monkeypatch.setattr(security_schema_normalization_gate, "ROOT", repo)
    monkeypatch.setattr(security_schema_normalization_gate, "evidence_root", lambda: repo / "evidence")
    assert security_schema_normalization_gate.main([]) == 0
    report = json.loads((sec / "security_schema_normalization_gate.json").read_text(encoding="utf-8"))
    assert report["summary"]["scanned_files"] == 2
    assert report["summary"]["normalized_files"] == 1
    assert report["summary"]["normalization_pct"] == 50.0


def test_security_schema_normalization_gate_strict_mode_fails_missing_keys(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    (sec / "a.json").write_text(json.dumps({"status": "PASS"}) + "\n", encoding="utf-8")
    monkeypatch.setattr(security_schema_normalization_gate, "ROOT", repo)
    monkeypatch.setattr(security_schema_normalization_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_SECURITY_SCHEMA_STRICT", "true")
    assert security_schema_normalization_gate.main([]) == 1
    report = json.loads((sec / "security_schema_normalization_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(item.startswith("missing_schema_version:") for item in report["findings"])
