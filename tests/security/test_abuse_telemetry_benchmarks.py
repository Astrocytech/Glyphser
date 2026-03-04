from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, sign_file
from tooling.security import abuse_telemetry_gate


def _write_policy(repo: Path) -> None:
    policy = repo / "governance" / "security" / "abuse_telemetry_policy.json"
    policy.parent.mkdir(parents=True, exist_ok=True)
    policy.write_text(
        json.dumps(
            {
                "runtime_api_state_path": "artifacts/generated/tmp/security/runtime_api_state.json",
                "profiles": {
                    "ci": {
                        "max_distinct_tokens": 4,
                        "max_auth_failures_per_token": 3,
                        "max_failure_spike": 8,
                    }
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    policy.with_suffix(".json.sig").write_text(sign_file(policy, key=current_key(strict=False)) + "\n", encoding="utf-8")


def _run_case(monkeypatch, tmp_path: Path, *, quotas: dict[str, object], expected_rc: int) -> None:
    repo = tmp_path / "repo"
    monkeypatch.setenv("GLYPHSER_ENV", "ci")
    monkeypatch.setenv("GLYPHSER_PROVENANCE_HMAC_KEY", "unit-test-signing-key")
    _write_policy(repo)
    state = repo / "artifacts" / "generated" / "tmp" / "security" / "runtime_api_state.json"
    state.parent.mkdir(parents=True, exist_ok=True)
    state.write_text(json.dumps({"quotas": quotas}) + "\n", encoding="utf-8")
    monkeypatch.setattr(abuse_telemetry_gate, "ROOT", repo)
    monkeypatch.setattr(abuse_telemetry_gate, "evidence_root", lambda: repo / "evidence")
    assert abuse_telemetry_gate.main([]) == expected_rc


def test_abuse_telemetry_benchmark_benign_near_threshold(monkeypatch, tmp_path: Path) -> None:
    _run_case(
        monkeypatch,
        tmp_path,
        quotas={
            "token_requests": {"a": 10, "b": 11, "c": 2, "d": 1},
            "auth_failures_by_token": {"a": 1, "b": 2, "c": 1, "d": 0},
        },
        expected_rc=0,
    )


def test_abuse_telemetry_benchmark_malicious_spray_and_spike(monkeypatch, tmp_path: Path) -> None:
    _run_case(
        monkeypatch,
        tmp_path,
        quotas={
            "token_requests": {"a": 1, "b": 1, "c": 1, "d": 1, "e": 1, "f": 1},
            "auth_failures_by_token": {"a": 5, "b": 3, "c": 4, "d": 1},
        },
        expected_rc=1,
    )
