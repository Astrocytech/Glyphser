from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_optimization_review_gate


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_security_optimization_review_gate_passes_with_fresh_affirmed_record(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    ev = repo / "evidence"
    _write(
        repo / "governance" / "security" / "security_optimization_review.json",
        {
            "reviewed_at_utc": "2026-03-01T00:00:00+00:00",
            "affirmed_no_security_semantics_change": True,
        },
    )
    monkeypatch.setattr(security_optimization_review_gate, "ROOT", repo)
    monkeypatch.setattr(
        security_optimization_review_gate,
        "REVIEW",
        repo / "governance" / "security" / "security_optimization_review.json",
    )
    monkeypatch.setattr(security_optimization_review_gate, "evidence_root", lambda: ev)
    monkeypatch.setenv("GLYPHSER_FIXED_UTC", "2026-03-05T00:00:00+00:00")
    assert security_optimization_review_gate.main([]) == 0


def test_security_optimization_review_gate_fails_when_review_stale_or_unaffirmed(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    ev = repo / "evidence"
    _write(
        repo / "governance" / "security" / "security_optimization_review.json",
        {
            "reviewed_at_utc": "2025-01-01T00:00:00+00:00",
            "affirmed_no_security_semantics_change": False,
        },
    )
    monkeypatch.setattr(security_optimization_review_gate, "ROOT", repo)
    monkeypatch.setattr(
        security_optimization_review_gate,
        "REVIEW",
        repo / "governance" / "security" / "security_optimization_review.json",
    )
    monkeypatch.setattr(security_optimization_review_gate, "evidence_root", lambda: ev)
    monkeypatch.setenv("GLYPHSER_FIXED_UTC", "2026-03-05T00:00:00+00:00")
    assert security_optimization_review_gate.main([]) == 1
    report = json.loads((ev / "security" / "security_optimization_review_gate.json").read_text(encoding="utf-8"))
    assert "optimization_review_missing_semantic_safety_affirmation" in report["findings"]
    assert any(str(item).startswith("optimization_review_stale:") for item in report["findings"])
