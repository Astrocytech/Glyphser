from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_evidence_corruption_gate


def test_security_evidence_corruption_gate_passes_for_valid_json(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    (sec / "a.json").write_text(json.dumps({"status": "PASS"}) + "\n", encoding="utf-8")
    monkeypatch.setattr(security_evidence_corruption_gate, "ROOT", repo)
    monkeypatch.setattr(security_evidence_corruption_gate, "evidence_root", lambda: repo / "evidence")
    assert security_evidence_corruption_gate.main([]) == 0


def test_security_evidence_corruption_gate_detects_truncated_payload(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    (sec / "bad.json").write_bytes(b'{"status":"PASS"')
    monkeypatch.setattr(security_evidence_corruption_gate, "ROOT", repo)
    monkeypatch.setattr(security_evidence_corruption_gate, "evidence_root", lambda: repo / "evidence")
    assert security_evidence_corruption_gate.main([]) == 1
    report = json.loads((sec / "security_evidence_corruption_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(item.startswith("invalid_json:") for item in report["findings"])
