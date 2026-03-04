from __future__ import annotations

import json
from pathlib import Path

from tooling.security import runtime_api_state_schema_gate


def _write_policy(repo: Path) -> None:
    (repo / "governance" / "security").mkdir(parents=True, exist_ok=True)
    (repo / "governance" / "security" / "abuse_telemetry_policy.json").write_text(
        json.dumps(
            {
                "runtime_api_state_path": "artifacts/generated/tmp/security/runtime_api_state.json",
                "required_runtime_counters": ["auth_failures_by_token", "token_requests", "job_replays"],
            }
        )
        + "\n",
        encoding="utf-8",
    )


def test_runtime_api_state_schema_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_policy(repo)
    state_dir = repo / "artifacts" / "generated" / "tmp" / "security"
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "runtime_api_state.json").write_text(
        json.dumps(
            {
                "quotas": {
                    "token_requests": {},
                    "token_submits": {},
                    "job_reads": {},
                    "job_replays": {},
                    "job_last_replay_ts": {},
                    "token_request_window": {},
                    "auth_failures_by_token": {},
                    "auth_failure_cooldown_until": {},
                    "replay_window_by_token": {},
                    "replay_window_by_job": {},
                    "replay_window_job_tokens": {},
                }
            }
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(runtime_api_state_schema_gate, "ROOT", repo)
    monkeypatch.setattr(runtime_api_state_schema_gate, "evidence_root", lambda: repo / "evidence")
    assert runtime_api_state_schema_gate.main([]) == 0


def test_runtime_api_state_schema_gate_fails_missing_keys(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_policy(repo)
    state_dir = repo / "artifacts" / "generated" / "tmp" / "security"
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "runtime_api_state.json").write_text(
        json.dumps({"quotas": {"token_requests": {}, "auth_failures_by_token": {}}}) + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(runtime_api_state_schema_gate, "ROOT", repo)
    monkeypatch.setattr(runtime_api_state_schema_gate, "evidence_root", lambda: repo / "evidence")
    assert runtime_api_state_schema_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "runtime_api_state_schema_gate.json").read_text("utf-8"))
    assert report["status"] == "FAIL"
    assert any(str(item).startswith("missing_quota_dict:") for item in report["findings"])
