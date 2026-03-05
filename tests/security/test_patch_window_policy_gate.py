from __future__ import annotations

import json
from pathlib import Path

from tooling.security import patch_window_policy_gate


def _write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_patch_window_policy_gate_passes_when_backfill_completed_within_window(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "patch_window_policy.json"
    log = repo / "governance" / "security" / "emergency_fix_backfill_log.json"
    _write(policy, {"max_backfill_days": 7, "backfill_log_path": "governance/security/emergency_fix_backfill_log.json"})
    _write(
        log,
        {
            "entries": [
                {
                    "id": "HF-1",
                    "applied_at_utc": "2026-03-01T00:00:00+00:00",
                    "tests_backfilled": True,
                    "docs_backfilled": True,
                    "backfilled_at_utc": "2026-03-03T00:00:00+00:00",
                }
            ]
        },
    )

    monkeypatch.setattr(patch_window_policy_gate, "ROOT", repo)
    monkeypatch.setattr(patch_window_policy_gate, "POLICY", policy)
    monkeypatch.setattr(patch_window_policy_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_FIXED_UTC", "2026-03-04T00:00:00+00:00")
    assert patch_window_policy_gate.main([]) == 0


def test_patch_window_policy_gate_fails_when_backfill_overdue(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "patch_window_policy.json"
    log = repo / "governance" / "security" / "emergency_fix_backfill_log.json"
    _write(policy, {"max_backfill_days": 3, "backfill_log_path": "governance/security/emergency_fix_backfill_log.json"})
    _write(
        log,
        {
            "entries": [
                {
                    "id": "HF-2",
                    "applied_at_utc": "2026-03-01T00:00:00+00:00",
                    "tests_backfilled": False,
                    "docs_backfilled": False,
                }
            ]
        },
    )

    monkeypatch.setattr(patch_window_policy_gate, "ROOT", repo)
    monkeypatch.setattr(patch_window_policy_gate, "POLICY", policy)
    monkeypatch.setattr(patch_window_policy_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_FIXED_UTC", "2026-03-10T00:00:00+00:00")
    assert patch_window_policy_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "patch_window_policy_gate.json").read_text(encoding="utf-8"))
    assert "patch_window_backfill_overdue:HF-2" in report["findings"]
