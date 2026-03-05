from __future__ import annotations

import json
from pathlib import Path

from tooling.security import stale_policy_review_gate


def test_stale_policy_review_gate_passes_for_fresh_metadata(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    meta = repo / "governance" / "security" / "metadata"
    meta.mkdir(parents=True)
    (meta / "THREAT_MODEL.meta.json").write_text(
        json.dumps(
            {
                "policy_version": "1.0.0",
                "last_reviewed_utc": "2026-03-01T00:00:00+00:00",
                "max_review_age_days": 180,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("GLYPHSER_FIXED_UTC", "2026-03-04T00:00:00+00:00")
    monkeypatch.setattr(stale_policy_review_gate, "ROOT", repo)
    monkeypatch.setattr(stale_policy_review_gate, "METADATA_DIR", meta)
    monkeypatch.setattr(stale_policy_review_gate, "evidence_root", lambda: repo / "evidence")
    assert stale_policy_review_gate.main([]) == 0


def test_stale_policy_review_gate_fails_for_stale_metadata(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    meta = repo / "governance" / "security" / "metadata"
    meta.mkdir(parents=True)
    (meta / "OPERATIONS.meta.json").write_text(
        json.dumps(
            {
                "policy_version": "1.0.0",
                "last_reviewed_utc": "2024-01-01T00:00:00+00:00",
                "max_review_age_days": 30,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("GLYPHSER_FIXED_UTC", "2026-03-04T00:00:00+00:00")
    monkeypatch.setattr(stale_policy_review_gate, "ROOT", repo)
    monkeypatch.setattr(stale_policy_review_gate, "METADATA_DIR", meta)
    monkeypatch.setattr(stale_policy_review_gate, "evidence_root", lambda: repo / "evidence")
    assert stale_policy_review_gate.main([]) == 1


def test_stale_policy_review_gate_fails_on_clock_consistency_violation(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    meta = repo / "governance" / "security" / "metadata"
    ev = repo / "evidence" / "security"
    meta.mkdir(parents=True)
    ev.mkdir(parents=True)
    (meta / "THREAT_MODEL.meta.json").write_text(
        json.dumps(
            {
                "policy_version": "1.0.0",
                "last_reviewed_utc": "2026-03-01T00:00:00+00:00",
                "max_review_age_days": 180,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("GLYPHSER_FIXED_UTC", "2026-03-04T00:00:00+00:00")
    monkeypatch.setattr(stale_policy_review_gate, "ROOT", repo)
    monkeypatch.setattr(stale_policy_review_gate, "METADATA_DIR", meta)
    monkeypatch.setattr(stale_policy_review_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(
        stale_policy_review_gate,
        "clock_consistency_violation",
        lambda _now: "clock_consistency_violation:wall_vs_monotonic_drift_seconds:13.000:tolerance_seconds:5.000",
    )
    assert stale_policy_review_gate.main([]) == 1
    report = json.loads((ev / "stale_policy_review_gate.json").read_text(encoding="utf-8"))
    assert any(str(item).startswith("clock_consistency_violation:") for item in report["findings"])
