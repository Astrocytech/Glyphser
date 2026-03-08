from __future__ import annotations

import json
from pathlib import Path

from tooling.security import rolling_merkle_checkpoints


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_rolling_merkle_checkpoints_generates_signed_report(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    _write(sec / "alpha.json", {"status": "PASS"})
    _write(sec / "beta.json", {"status": "PASS", "count": 2})

    monkeypatch.setattr(rolling_merkle_checkpoints, "ROOT", repo)
    monkeypatch.setattr(rolling_merkle_checkpoints, "evidence_root", lambda: repo / "evidence")
    assert rolling_merkle_checkpoints.main([]) == 0

    report = json.loads((sec / "rolling_merkle_checkpoints.json").read_text(encoding="utf-8"))
    gate = json.loads((sec / "rolling_merkle_checkpoints_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert report["summary"]["artifact_count"] == 2
    assert len(report["checkpoints"]) == 2
    assert len(report["summary"]["final_root"]) == 64
    assert gate["status"] == "PASS"
    assert (sec / "rolling_merkle_checkpoints.json.sig").exists()


def test_rolling_merkle_checkpoints_fails_without_artifacts(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(rolling_merkle_checkpoints, "ROOT", repo)
    monkeypatch.setattr(rolling_merkle_checkpoints, "evidence_root", lambda: repo / "evidence")
    assert rolling_merkle_checkpoints.main([]) == 1

    gate = json.loads((sec / "rolling_merkle_checkpoints_gate.json").read_text(encoding="utf-8"))
    assert gate["status"] == "FAIL"
    assert "missing_security_artifacts" in gate["findings"]
