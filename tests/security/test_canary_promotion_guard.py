from __future__ import annotations

import json
from pathlib import Path

from tooling.security import canary_promotion_guard


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_policy(repo: Path) -> None:
    _write(
        repo / "governance" / "security" / "promotion_policy.json",
        {
            "required_reports": ["policy_signature.json"],
            "canary_required_reports": ["policy_signature.json", "provenance_signature.json"],
            "allow_signed_override": True,
        },
    )


def test_canary_promotion_guard_passes_when_canary_reports_pass(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_policy(repo)
    sec = repo / "evidence" / "security"
    _write(sec / "policy_signature.json", {"status": "PASS"})
    _write(sec / "provenance_signature.json", {"status": "PASS"})
    monkeypatch.setattr(canary_promotion_guard, "ROOT", repo)
    monkeypatch.setattr(canary_promotion_guard, "POLICY", repo / "governance/security/promotion_policy.json")
    monkeypatch.setattr(canary_promotion_guard, "evidence_root", lambda: repo / "evidence")
    assert canary_promotion_guard.main([]) == 0


def test_canary_promotion_guard_fails_when_canary_report_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_policy(repo)
    sec = repo / "evidence" / "security"
    _write(sec / "policy_signature.json", {"status": "PASS"})
    monkeypatch.setattr(canary_promotion_guard, "ROOT", repo)
    monkeypatch.setattr(canary_promotion_guard, "POLICY", repo / "governance/security/promotion_policy.json")
    monkeypatch.setattr(canary_promotion_guard, "evidence_root", lambda: repo / "evidence")
    assert canary_promotion_guard.main([]) == 1
