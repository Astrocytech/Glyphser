from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, sign_file
from tooling.security import abuse_telemetry_gate


def test_abuse_telemetry_gate_passes_within_threshold(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "governance" / "security").mkdir(parents=True)
    (repo / "artifacts" / "generated" / "tmp" / "security").mkdir(parents=True)
    policy = repo / "governance" / "security" / "abuse_telemetry_policy.json"
    policy.write_text(
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
    policy.with_suffix(".json.sig").write_text(sign_file(policy, key=current_key(strict=False)) + "\n", encoding="utf-8")
    (repo / "artifacts" / "generated" / "tmp" / "security" / "runtime_api_state.json").write_text(
        json.dumps(
            {
                "quotas": {"token_requests": {"a": 2, "b": 1}, "auth_failures_by_token": {"a": 1}},
                "jobs": {"j1": {"trace_id": "trace-1"}},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(abuse_telemetry_gate, "ROOT", repo)
    monkeypatch.setattr(abuse_telemetry_gate, "evidence_root", lambda: repo / "evidence")
    assert abuse_telemetry_gate.main([]) == 0
    report = json.loads((repo / "evidence" / "security" / "abuse_telemetry.json").read_text(encoding="utf-8"))
    assert report["summary"]["correlation_ids"] == ["trace-1"]
    assert report["summary"]["correlation_id_count"] == 1


def test_abuse_telemetry_gate_fails_on_token_spray(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "governance" / "security").mkdir(parents=True)
    (repo / "artifacts" / "generated" / "tmp" / "security").mkdir(parents=True)
    policy = repo / "governance" / "security" / "abuse_telemetry_policy.json"
    policy.write_text(
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
    policy.with_suffix(".json.sig").write_text(sign_file(policy, key=current_key(strict=False)) + "\n", encoding="utf-8")
    (repo / "artifacts" / "generated" / "tmp" / "security" / "runtime_api_state.json").write_text(
        json.dumps({"quotas": {"token_requests": {"a": 2, "b": 1}, "auth_failures_by_token": {"a": 5}}}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(abuse_telemetry_gate, "ROOT", repo)
    monkeypatch.setattr(abuse_telemetry_gate, "evidence_root", lambda: repo / "evidence")
    assert abuse_telemetry_gate.main([]) == 1


def test_abuse_telemetry_gate_fails_on_bad_policy_signature(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "governance" / "security").mkdir(parents=True)
    (repo / "artifacts" / "generated" / "tmp" / "security").mkdir(parents=True)
    policy = repo / "governance" / "security" / "abuse_telemetry_policy.json"
    policy.write_text(
        json.dumps(
            {
                "runtime_api_state_path": "artifacts/generated/tmp/security/runtime_api_state.json",
                "max_distinct_tokens": 10,
                "max_auth_failures_per_token": 10,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    policy.with_suffix(".json.sig").write_text("bad-signature\n", encoding="utf-8")
    (repo / "artifacts" / "generated" / "tmp" / "security" / "runtime_api_state.json").write_text(
        json.dumps({"quotas": {"token_requests": {}, "auth_failures_by_token": {}}}) + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(abuse_telemetry_gate, "ROOT", repo)
    monkeypatch.setattr(abuse_telemetry_gate, "evidence_root", lambda: repo / "evidence")
    try:
        abuse_telemetry_gate.main([])
    except ValueError as exc:
        assert "signature" in str(exc)
    else:
        raise AssertionError("expected signature verification failure")
