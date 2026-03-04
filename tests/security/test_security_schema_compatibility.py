from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_schema_normalization_gate


def _write(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def test_schema_normalization_gate_allows_legacy_and_normalized_coexistence(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    _write(sec / "legacy_gate.json", {"status": "PASS"})
    _write(
        sec / "normalized_gate.json",
        {
            "status": "PASS",
            "schema_version": 1,
            "findings": [],
            "summary": {},
            "metadata": {"gate": "normalized"},
        },
    )

    monkeypatch.setattr(security_schema_normalization_gate, "ROOT", repo)
    monkeypatch.setattr(security_schema_normalization_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.delenv("GLYPHSER_SECURITY_SCHEMA_STRICT", raising=False)
    assert security_schema_normalization_gate.main([]) == 0
    report = json.loads((sec / "security_schema_normalization_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert report["summary"]["scanned_files"] == 2
    assert report["summary"]["normalized_files"] == 1


def test_schema_normalization_gate_strict_mode_blocks_legacy_reports(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    _write(sec / "legacy_gate.json", {"status": "PASS"})

    monkeypatch.setattr(security_schema_normalization_gate, "ROOT", repo)
    monkeypatch.setattr(security_schema_normalization_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_SECURITY_SCHEMA_STRICT", "1")
    assert security_schema_normalization_gate.main([]) == 1
    report = json.loads((sec / "security_schema_normalization_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(str(item).startswith("missing_schema_version:legacy_gate.json") for item in report["findings"])
