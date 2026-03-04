from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_cross_gate_consistency_gate


def test_security_cross_gate_consistency_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    (sec / "security_super_gate.json").write_text(
        json.dumps(
            {
                "results": [
                    {"cmd": ["python", "tooling/security/workflow_risky_patterns_gate.py"], "status": "PASS"}
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (sec / "workflow_risky_patterns_gate.json").write_text('{"status":"PASS"}\n', encoding="utf-8")
    monkeypatch.setattr(security_cross_gate_consistency_gate, "evidence_root", lambda: repo / "evidence")
    assert security_cross_gate_consistency_gate.main([]) == 0


def test_security_cross_gate_consistency_gate_fails_on_mismatch(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    (sec / "security_super_gate.json").write_text(
        json.dumps(
            {"results": [{"cmd": ["python", "tooling/security/workflow_risky_patterns_gate.py"], "status": "PASS"}]}
        )
        + "\n",
        encoding="utf-8",
    )
    (sec / "workflow_risky_patterns_gate.json").write_text('{"status":"FAIL"}\n', encoding="utf-8")
    monkeypatch.setattr(security_cross_gate_consistency_gate, "evidence_root", lambda: repo / "evidence")
    assert security_cross_gate_consistency_gate.main([]) == 1
