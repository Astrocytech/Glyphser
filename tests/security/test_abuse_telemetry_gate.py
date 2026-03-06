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


def test_abuse_telemetry_gate_fails_when_thresholds_loosened_without_signed_approval(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    gov = repo / "governance" / "security"
    gov.mkdir(parents=True)
    (repo / "artifacts" / "generated" / "tmp" / "security").mkdir(parents=True)
    policy = gov / "abuse_telemetry_policy.json"
    policy.write_text(
        json.dumps(
            {
                "runtime_api_state_path": "artifacts/generated/tmp/security/runtime_api_state.json",
                "max_distinct_tokens": 10,
                "max_auth_failures_per_token": 10,
                "max_failure_spike": 10,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    policy.with_suffix(".json.sig").write_text(sign_file(policy, key=current_key(strict=False)) + "\n", encoding="utf-8")
    baseline = gov / "abuse_telemetry_threshold_baseline.json"
    baseline.write_text(
        json.dumps({"max_distinct_tokens": 5, "max_auth_failures_per_token": 5, "max_failure_spike": 5}) + "\n",
        encoding="utf-8",
    )
    (repo / "artifacts" / "generated" / "tmp" / "security" / "runtime_api_state.json").write_text(
        json.dumps({"quotas": {"token_requests": {}, "auth_failures_by_token": {}}}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(abuse_telemetry_gate, "ROOT", repo)
    monkeypatch.setattr(abuse_telemetry_gate, "BASELINE_PATH", baseline)
    monkeypatch.setattr(abuse_telemetry_gate, "THRESHOLD_APPROVAL_PATH", gov / "abuse_threshold_change_approval.json")
    monkeypatch.setattr(abuse_telemetry_gate, "evidence_root", lambda: repo / "evidence")
    assert abuse_telemetry_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "abuse_telemetry.json").read_text(encoding="utf-8"))
    assert any(str(item).startswith("threshold_loosened_without_signed_approval:") for item in report["findings"])


def test_abuse_telemetry_gate_allows_loosened_thresholds_with_signed_approval(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    gov = repo / "governance" / "security"
    gov.mkdir(parents=True)
    (repo / "artifacts" / "generated" / "tmp" / "security").mkdir(parents=True)
    policy = gov / "abuse_telemetry_policy.json"
    policy.write_text(
        json.dumps(
            {
                "runtime_api_state_path": "artifacts/generated/tmp/security/runtime_api_state.json",
                "max_distinct_tokens": 10,
                "max_auth_failures_per_token": 10,
                "max_failure_spike": 10,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    policy.with_suffix(".json.sig").write_text(sign_file(policy, key=current_key(strict=False)) + "\n", encoding="utf-8")
    baseline = gov / "abuse_telemetry_threshold_baseline.json"
    baseline.write_text(
        json.dumps({"max_distinct_tokens": 5, "max_auth_failures_per_token": 5, "max_failure_spike": 5}) + "\n",
        encoding="utf-8",
    )
    approval = gov / "abuse_threshold_change_approval.json"
    rollout = repo / "evidence" / "security" / "quota_rollout_stage_ci.json"
    rollout.parent.mkdir(parents=True, exist_ok=True)
    rollout.write_text(json.dumps({"status": "PASS", "stage": "ci_canary"}) + "\n", encoding="utf-8")
    approval.write_text(
        json.dumps(
            {
                "approved_relaxations": [
                    "ci:max_distinct_tokens:5->10",
                    "ci:max_auth_failures_per_token:5->10",
                    "ci:max_failure_spike:5->10",
                ],
                "staged_rollout_evidence": ["evidence/security/quota_rollout_stage_ci.json"],
                "approved_by": "security-lead",
                "ticket": "SEC-123",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    approval.with_suffix(".json.sig").write_text(sign_file(approval, key=current_key(strict=False)) + "\n", encoding="utf-8")
    (repo / "artifacts" / "generated" / "tmp" / "security" / "runtime_api_state.json").write_text(
        json.dumps({"quotas": {"token_requests": {}, "auth_failures_by_token": {}}}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(abuse_telemetry_gate, "ROOT", repo)
    monkeypatch.setattr(abuse_telemetry_gate, "BASELINE_PATH", baseline)
    monkeypatch.setattr(abuse_telemetry_gate, "THRESHOLD_APPROVAL_PATH", approval)
    monkeypatch.setattr(abuse_telemetry_gate, "evidence_root", lambda: repo / "evidence")
    assert abuse_telemetry_gate.main([]) == 0


def test_abuse_telemetry_gate_fails_when_relaxation_rollout_evidence_missing(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    gov = repo / "governance" / "security"
    gov.mkdir(parents=True)
    (repo / "artifacts" / "generated" / "tmp" / "security").mkdir(parents=True)
    policy = gov / "abuse_telemetry_policy.json"
    policy.write_text(
        json.dumps(
            {
                "runtime_api_state_path": "artifacts/generated/tmp/security/runtime_api_state.json",
                "max_distinct_tokens": 10,
                "max_auth_failures_per_token": 10,
                "max_failure_spike": 10,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    policy.with_suffix(".json.sig").write_text(sign_file(policy, key=current_key(strict=False)) + "\n", encoding="utf-8")
    baseline = gov / "abuse_telemetry_threshold_baseline.json"
    baseline.write_text(
        json.dumps({"max_distinct_tokens": 5, "max_auth_failures_per_token": 5, "max_failure_spike": 5}) + "\n",
        encoding="utf-8",
    )
    approval = gov / "abuse_threshold_change_approval.json"
    approval.write_text(
        json.dumps(
            {
                "approved_relaxations": [
                    "ci:max_distinct_tokens:5->10",
                    "ci:max_auth_failures_per_token:5->10",
                    "ci:max_failure_spike:5->10",
                ],
                "staged_rollout_evidence": ["evidence/security/missing_rollout_artifact.json"],
                "approved_by": "security-lead",
                "ticket": "SEC-999",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    approval.with_suffix(".json.sig").write_text(sign_file(approval, key=current_key(strict=False)) + "\n", encoding="utf-8")
    (repo / "artifacts" / "generated" / "tmp" / "security" / "runtime_api_state.json").write_text(
        json.dumps({"quotas": {"token_requests": {}, "auth_failures_by_token": {}}}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(abuse_telemetry_gate, "ROOT", repo)
    monkeypatch.setattr(abuse_telemetry_gate, "BASELINE_PATH", baseline)
    monkeypatch.setattr(abuse_telemetry_gate, "THRESHOLD_APPROVAL_PATH", approval)
    monkeypatch.setattr(abuse_telemetry_gate, "evidence_root", lambda: repo / "evidence")
    assert abuse_telemetry_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "abuse_telemetry.json").read_text(encoding="utf-8"))
    assert any(
        str(item).startswith("threshold_relaxation_missing_rollout_evidence:missing_staged_rollout_evidence:")
        or str(item).startswith("threshold_relaxation_missing_rollout_evidence:missing_staged_rollout_evidence")
        for item in report["findings"]
    )


def test_abuse_telemetry_gate_captures_role_and_source_dimensions(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    gov = repo / "governance" / "security"
    gov.mkdir(parents=True)
    state_dir = repo / "artifacts" / "generated" / "tmp" / "security"
    state_dir.mkdir(parents=True)
    policy = gov / "abuse_telemetry_policy.json"
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
    policy.with_suffix(".json.sig").write_text(sign_file(policy, key=current_key(strict=False)) + "\n", encoding="utf-8")
    (state_dir / "runtime_api_state.json").write_text(
        json.dumps({"quotas": {"token_requests": {"role:operator": 2}, "auth_failures_by_token": {"role:viewer": 1}}})
        + "\n",
        encoding="utf-8",
    )
    (state_dir / "audit.log.jsonl").write_text(
        json.dumps({"operation": "submit", "role_token_kind": "role"}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(abuse_telemetry_gate, "ROOT", repo)
    monkeypatch.setattr(abuse_telemetry_gate, "evidence_root", lambda: repo / "evidence")
    assert abuse_telemetry_gate.main([]) == 0
    report = json.loads((repo / "evidence" / "security" / "abuse_telemetry.json").read_text(encoding="utf-8"))
    assert report["summary"]["token_role_dimensions"] == {"operator": 1, "viewer": 1}
    assert report["summary"]["token_source_dimensions"] == {"role": 1}


def test_abuse_telemetry_gate_fails_when_audit_source_dimension_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    gov = repo / "governance" / "security"
    gov.mkdir(parents=True)
    state_dir = repo / "artifacts" / "generated" / "tmp" / "security"
    state_dir.mkdir(parents=True)
    policy = gov / "abuse_telemetry_policy.json"
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
    policy.with_suffix(".json.sig").write_text(sign_file(policy, key=current_key(strict=False)) + "\n", encoding="utf-8")
    (state_dir / "runtime_api_state.json").write_text(
        json.dumps({"quotas": {"token_requests": {"role:operator": 1}, "auth_failures_by_token": {}}}) + "\n",
        encoding="utf-8",
    )
    (state_dir / "audit.log.jsonl").write_text(
        json.dumps({"operation": "submit", "scope": "jobs:write"}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(abuse_telemetry_gate, "ROOT", repo)
    monkeypatch.setattr(abuse_telemetry_gate, "evidence_root", lambda: repo / "evidence")
    assert abuse_telemetry_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "abuse_telemetry.json").read_text(encoding="utf-8"))
    assert "missing_token_source_dimension" in report["findings"]
