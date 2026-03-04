from __future__ import annotations

import json
from pathlib import Path

from tooling.security import live_rollout_gate


def test_live_rollout_gate_passes_with_live_evidence(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "governance" / "security").mkdir(parents=True)
    (repo / "evidence" / "security").mkdir(parents=True)
    (repo / "governance" / "security" / "live_rollout_policy.json").write_text(
        json.dumps({"max_evidence_age_hours": 9999}) + "\n",
        encoding="utf-8",
    )
    branch_payload = {"status": "PASS", "mode": "live", "checked_at_utc": "2026-03-04T00:00:00+00:00"}
    integ_payload = {"status": "PASS", "mode": "live", "checked_at_utc": "2026-03-04T00:00:00+00:00"}
    (repo / "evidence" / "security" / "branch_protection_live.json").write_text(
        json.dumps(branch_payload) + "\n",
        encoding="utf-8",
    )
    (repo / "evidence" / "security" / "live_integrations.json").write_text(
        json.dumps(integ_payload) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(live_rollout_gate, "ROOT", repo)
    monkeypatch.setattr(live_rollout_gate, "evidence_root", lambda: repo / "evidence")
    assert live_rollout_gate.main([]) == 0


def test_live_rollout_gate_fails_on_dry_run_when_strict(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "governance" / "security").mkdir(parents=True)
    (repo / "evidence" / "security").mkdir(parents=True)
    (repo / "governance" / "security" / "live_rollout_policy.json").write_text(
        json.dumps({"max_evidence_age_hours": 9999}) + "\n",
        encoding="utf-8",
    )
    payload = {"status": "PASS", "mode": "dry_run", "checked_at_utc": "2026-03-04T00:00:00+00:00"}
    (repo / "evidence" / "security" / "live_integrations.json").write_text(
        json.dumps(payload) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(live_rollout_gate, "ROOT", repo)
    monkeypatch.setattr(live_rollout_gate, "evidence_root", lambda: repo / "evidence")
    assert live_rollout_gate.main(["--target", "live_integrations"]) == 1


def test_live_rollout_gate_fails_on_missing_evidence(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "governance" / "security").mkdir(parents=True)
    (repo / "governance" / "security" / "live_rollout_policy.json").write_text(
        json.dumps({"max_evidence_age_hours": 24}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(live_rollout_gate, "ROOT", repo)
    monkeypatch.setattr(live_rollout_gate, "evidence_root", lambda: repo / "evidence")
    assert live_rollout_gate.main(["--target", "branch_protection"]) == 1


def test_live_rollout_gate_fails_on_stale_evidence(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "governance" / "security").mkdir(parents=True)
    (repo / "evidence" / "security").mkdir(parents=True)
    (repo / "governance" / "security" / "live_rollout_policy.json").write_text(
        json.dumps({"max_evidence_age_hours": 1}) + "\n",
        encoding="utf-8",
    )
    payload = {"status": "PASS", "mode": "live", "checked_at_utc": "2000-01-01T00:00:00+00:00"}
    (repo / "evidence" / "security" / "live_integrations.json").write_text(
        json.dumps(payload) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(live_rollout_gate, "ROOT", repo)
    monkeypatch.setattr(live_rollout_gate, "evidence_root", lambda: repo / "evidence")
    assert live_rollout_gate.main(["--target", "live_integrations"]) == 1
