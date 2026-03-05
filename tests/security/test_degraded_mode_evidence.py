from __future__ import annotations

import json
from pathlib import Path

from tooling.security import degraded_mode_evidence


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_degraded_mode_evidence_passes_without_fallback_events(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    monkeypatch.setattr(degraded_mode_evidence, "ROOT", repo)
    monkeypatch.setattr(degraded_mode_evidence, "evidence_root", lambda: repo / "evidence")
    assert degraded_mode_evidence.main([]) == 0
    report = json.loads((repo / "evidence" / "security" / "degraded_mode_evidence.json").read_text("utf-8"))
    assert report["status"] == "PASS"
    assert report["findings"] == []


def test_degraded_mode_evidence_warns_when_override_or_fallback_observed(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    _write(sec / "promotion_policy_gate.json", {"summary": {"override_applied": True}})
    _write(sec / "key_provenance_continuity_gate.json", {"findings": ["fallback_signing_used:policy_signature"]})
    monkeypatch.setattr(degraded_mode_evidence, "ROOT", repo)
    monkeypatch.setattr(degraded_mode_evidence, "evidence_root", lambda: repo / "evidence")
    assert degraded_mode_evidence.main([]) == 0
    report = json.loads((repo / "evidence" / "security" / "degraded_mode_evidence.json").read_text("utf-8"))
    assert report["status"] == "WARN"
    assert "promotion_signed_override_applied" in report["findings"]
