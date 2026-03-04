from __future__ import annotations

import json
from pathlib import Path

from tooling.security import abuse_telemetry_gate


def test_abuse_telemetry_gate_passes_within_threshold(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "governance" / "security").mkdir(parents=True)
    (repo / "artifacts" / "generated" / "tmp" / "security").mkdir(parents=True)
    (repo / "governance" / "security" / "abuse_telemetry_policy.json").write_text(
        json.dumps(
            {
                "runtime_api_state_path": "artifacts/generated/tmp/security/runtime_api_state.json",
                "max_distinct_tokens": 5,
                "max_auth_failures_per_token": 3,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (repo / "artifacts" / "generated" / "tmp" / "security" / "runtime_api_state.json").write_text(
        json.dumps({"quotas": {"token_requests": {"a": 2, "b": 1}, "auth_failures_by_token": {"a": 1}}}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(abuse_telemetry_gate, "ROOT", repo)
    monkeypatch.setattr(abuse_telemetry_gate, "evidence_root", lambda: repo / "evidence")
    assert abuse_telemetry_gate.main([]) == 0


def test_abuse_telemetry_gate_fails_on_token_spray(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "governance" / "security").mkdir(parents=True)
    (repo / "artifacts" / "generated" / "tmp" / "security").mkdir(parents=True)
    (repo / "governance" / "security" / "abuse_telemetry_policy.json").write_text(
        json.dumps(
            {
                "runtime_api_state_path": "artifacts/generated/tmp/security/runtime_api_state.json",
                "max_distinct_tokens": 1,
                "max_auth_failures_per_token": 1,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (repo / "artifacts" / "generated" / "tmp" / "security" / "runtime_api_state.json").write_text(
        json.dumps({"quotas": {"token_requests": {"a": 2, "b": 1}, "auth_failures_by_token": {"a": 5}}}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(abuse_telemetry_gate, "ROOT", repo)
    monkeypatch.setattr(abuse_telemetry_gate, "evidence_root", lambda: repo / "evidence")
    assert abuse_telemetry_gate.main([]) == 1
