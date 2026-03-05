from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_gate_parity_compare, security_gate_parity_snapshot


def _write_report(path: Path, *, status: str, findings: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"status": status, "findings": findings}) + "\n", encoding="utf-8")


def test_security_gate_parity_snapshot_writes_deterministic_hash(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    for name in security_gate_parity_snapshot.TARGET_REPORTS:
        _write_report(sec / name, status="PASS", findings=[])
    monkeypatch.setattr(security_gate_parity_snapshot, "ROOT", repo)
    monkeypatch.setattr(security_gate_parity_snapshot, "evidence_root", lambda: repo / "evidence")
    assert security_gate_parity_snapshot.main([]) == 0
    payload = json.loads((sec / "security_gate_parity_snapshot.json").read_text(encoding="utf-8"))
    assert payload["parity_hash"]
    assert payload["missing_reports"] == []


def test_security_gate_parity_compare_detects_mismatch(tmp_path: Path) -> None:
    left = tmp_path / "left.json"
    right = tmp_path / "right.json"
    left.write_text(json.dumps({"parity_hash": "a"}) + "\n", encoding="utf-8")
    right.write_text(json.dumps({"parity_hash": "b"}) + "\n", encoding="utf-8")
    assert security_gate_parity_compare.main(["--left", str(left), "--right", str(right)]) == 1
    right.write_text(json.dumps({"parity_hash": "a"}) + "\n", encoding="utf-8")
    assert security_gate_parity_compare.main(["--left", str(left), "--right", str(right)]) == 0
