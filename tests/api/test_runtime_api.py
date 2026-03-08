from __future__ import annotations

import base64
from concurrent.futures import ThreadPoolExecutor
import hashlib
import hmac
import json
import time
from pathlib import Path

from runtime.glyphser.api.runtime_api import RuntimeApiConfig, RuntimeApiService

ROOT = Path(__file__).resolve().parents[2]


def _signed_token(
    *,
    key: str,
    scope: str,
    aud: str,
    roles: list[str] | None = None,
    jti: str = "jti-1",
    exp: int | None = None,
    iss: str = "glyphser-runtime",
) -> str:
    payload = {
        "iss": iss,
        "sub": "test-subject",
        "scope": scope,
        "aud": aud,
        "exp": int(time.time()) + 3600 if exp is None else int(exp),
        "jti": jti,
        "roles": roles or ["operator"],
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    payload_b64 = base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")
    sig = hmac.new(key.encode("utf-8"), payload_b64.encode("ascii"), hashlib.sha256).hexdigest()
    return f"sig:{payload_b64}.{sig}"


def test_submit_idempotency_and_status(tmp_path: Path):
    svc = RuntimeApiService(RuntimeApiConfig(root=ROOT, state_path=tmp_path / "state.json"))
    payload = {"payload": {"job": "demo", "value": 1}}
    first = svc.submit_job(payload=payload, token="token-a", scope="jobs:write", idempotency_key="abc")
    second = svc.submit_job(payload=payload, token="token-a", scope="jobs:write", idempotency_key="abc")
    assert first["job_id"] == second["job_id"]
    status = svc.status(first["job_id"], token="token-a", scope="jobs:read")
    assert status["status"] == "accepted"
    assert status["api_version"] == "1.0.0"


def test_idempotency_collision_records_provenance(tmp_path: Path) -> None:
    svc = RuntimeApiService(RuntimeApiConfig(root=ROOT, state_path=tmp_path / "state.json"))
    first = svc.submit_job(payload={"payload": {"job": "a"}}, token="token-a", scope="jobs:write", idempotency_key="abc")
    second = svc.submit_job(payload={"payload": {"job": "b"}}, token="token-b", scope="jobs:write", idempotency_key="abc")
    assert first["job_id"] == second["job_id"]
    state = json.loads((tmp_path / "state.json").read_text(encoding="utf-8"))
    collisions = ((state.get("quotas") or {}) if isinstance(state, dict) else {}).get("idempotency_collisions", {})
    assert isinstance(collisions, dict)
    assert int(collisions.get("abc", 0)) >= 1
    provenance = state.get("collision_provenance", {})
    assert isinstance(provenance, dict)
    assert provenance
    first_entry = next(iter(provenance.values()))
    assert isinstance(first_entry, dict)
    assert first_entry.get("idempotency_key") == "abc"
    assert str(first_entry.get("existing_payload_hash", "")) != str(first_entry.get("incoming_payload_hash", ""))


def test_evidence_and_replay(tmp_path: Path):
    root = tmp_path / "repo"
    (root / "evidence" / "conformance" / "reports").mkdir(parents=True)
    (root / "artifacts" / "bundles").mkdir(parents=True)
    (root / "evidence" / "repro").mkdir(parents=True)
    (root / "evidence" / "conformance" / "reports" / "latest.json").write_text(
        json.dumps({"status": "PASS"}) + "\n", encoding="utf-8"
    )
    line = "abc123  hello-core-bundle.tar.gz\n"
    (root / "artifacts" / "bundles" / "hello-core-bundle.sha256").write_text(line, encoding="utf-8")
    (root / "evidence" / "repro" / "hashes.txt").write_text(line, encoding="utf-8")
    svc = RuntimeApiService(RuntimeApiConfig(root=root, state_path=tmp_path / "state.json"))
    job = svc.submit_job(payload={"payload": {"n": 1}}, token="token-a", scope="jobs:write")
    ev = svc.evidence(job["job_id"], token="token-a", scope="evidence:read")
    assert ev["bundle_manifest_line"] == "abc123  hello-core-bundle.tar.gz"
    replay = svc.replay(job["job_id"], token="token-a", scope="replay:run")
    assert replay["replay_verdict"] == "PASS"


def test_submit_rejects_unauthorized_role(tmp_path: Path):
    audit_path = tmp_path / "audit.log.jsonl"
    svc = RuntimeApiService(RuntimeApiConfig(root=ROOT, state_path=tmp_path / "state.json", audit_log_path=audit_path))
    try:
        svc.submit_job(payload={"payload": {"x": 1}}, token="role:viewer", scope="jobs:write")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "unauthorized action" in str(exc)
    state = json.loads((tmp_path / "state.json").read_text(encoding="utf-8"))
    failures = state.get("quotas", {}).get("auth_failures_by_token", {})
    assert failures.get("role:viewer", 0) >= 1
    line = audit_path.read_text(encoding="utf-8").strip().splitlines()[-1]
    event = json.loads(line)["event"]
    assert event.get("auth_error_code") == "AUTH_UNAUTHORIZED_ACTION"


def test_submit_rejects_payload_too_large(tmp_path: Path):
    svc = RuntimeApiService(RuntimeApiConfig(root=ROOT, state_path=tmp_path / "state.json"))
    payload = {"payload": {"blob": "x" * (130 * 1024)}}
    try:
        svc.submit_job(payload=payload, token="token-a", scope="jobs:write")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "payload too large" in str(exc)


def test_submit_payload_max_bytes_is_configurable(tmp_path: Path):
    svc = RuntimeApiService(
        RuntimeApiConfig(root=ROOT, state_path=tmp_path / "state.json", submit_payload_max_bytes=64)
    )
    payload = {"payload": {"blob": "x" * 1024}}
    try:
        svc.submit_job(payload=payload, token="token-a", scope="jobs:write")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "payload too large" in str(exc)


def test_submit_rejects_payload_too_deep(tmp_path: Path):
    svc = RuntimeApiService(RuntimeApiConfig(root=ROOT, state_path=tmp_path / "state.json"))
    payload: dict[str, object] = {"n0": {}}
    cursor = payload["n0"]
    assert isinstance(cursor, dict)
    for ix in range(20):
        cursor[f"n{ix + 1}"] = {}
        nxt = cursor[f"n{ix + 1}"]
        assert isinstance(nxt, dict)
        cursor = nxt
    try:
        svc.submit_job(payload=payload, token="token-a", scope="jobs:write")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "payload too deeply nested" in str(exc)


def test_submit_payload_max_depth_is_configurable(tmp_path: Path):
    svc = RuntimeApiService(
        RuntimeApiConfig(root=ROOT, state_path=tmp_path / "state.json", submit_payload_max_depth=2)
    )
    payload = {"payload": {"a": {"b": {"c": 1}}}}
    try:
        svc.submit_job(payload=payload, token="token-a", scope="jobs:write")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "payload too deeply nested" in str(exc)


def test_submit_payload_max_items_is_configurable(tmp_path: Path):
    svc = RuntimeApiService(
        RuntimeApiConfig(root=ROOT, state_path=tmp_path / "state.json", submit_payload_max_items=5)
    )
    payload = {"payload": {f"k{i}": i for i in range(10)}}
    try:
        svc.submit_job(payload=payload, token="token-a", scope="jobs:write")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "payload too complex" in str(exc)


def test_submit_rejects_long_idempotency_key(tmp_path: Path):
    svc = RuntimeApiService(RuntimeApiConfig(root=ROOT, state_path=tmp_path / "state.json"))
    long_key = "k" * 129
    try:
        svc.submit_job(
            payload={"payload": {"x": 1}},
            token="token-a",
            scope="jobs:write",
            idempotency_key=long_key,
        )
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "idempotency_key too long" in str(exc)


def test_submit_rejects_invalid_idempotency_key_chars(tmp_path: Path):
    svc = RuntimeApiService(RuntimeApiConfig(root=ROOT, state_path=tmp_path / "state.json"))
    try:
        svc.submit_job(
            payload={"payload": {"x": 1}},
            token="token-a",
            scope="jobs:write",
            idempotency_key="bad key with spaces",
        )
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "idempotency_key has invalid characters" in str(exc)


def test_submit_rejects_unknown_top_level_fields(tmp_path: Path):
    svc = RuntimeApiService(RuntimeApiConfig(root=ROOT, state_path=tmp_path / "state.json"))
    try:
        svc.submit_job(
            payload={"payload": {"x": 1}, "extra": {"y": 2}},
            token="token-a",
            scope="jobs:write",
        )
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "unknown keys" in str(exc)


def test_submit_payload_canonicalization_is_deterministic(tmp_path: Path):
    svc = RuntimeApiService(RuntimeApiConfig(root=ROOT, state_path=tmp_path / "state.json"))
    a = svc.submit_job(payload={"payload": {"x": 1, "y": 2}}, token="token-a", scope="jobs:write")
    b = svc.submit_job(payload={"payload": {"y": 2, "x": 1}}, token="token-a", scope="jobs:write")
    assert a["job_id"] == b["job_id"]
    assert a["payload_hash"] == b["payload_hash"]


def test_scope_allowlist_enforced(tmp_path: Path):
    svc = RuntimeApiService(RuntimeApiConfig(root=ROOT, state_path=tmp_path / "state.json"))
    try:
        svc.submit_job(payload={"payload": {"x": 1}}, token="token-a", scope="jobs:read")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "invalid scope" in str(exc)


def test_status_scope_allowlist_enforced(tmp_path: Path):
    svc = RuntimeApiService(RuntimeApiConfig(root=ROOT, state_path=tmp_path / "state.json"))
    job = svc.submit_job(payload={"payload": {"x": 1}}, token="token-a", scope="jobs:write")
    try:
        svc.status(job["job_id"], token="token-a", scope="evidence:read")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "invalid scope" in str(exc)


def test_evidence_scope_allowlist_enforced(tmp_path: Path):
    svc = RuntimeApiService(RuntimeApiConfig(root=ROOT, state_path=tmp_path / "state.json"))
    job = svc.submit_job(payload={"payload": {"x": 1}}, token="token-a", scope="jobs:write")
    try:
        svc.evidence(job["job_id"], token="token-a", scope="jobs:read")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "invalid scope" in str(exc)


def test_replay_scope_allowlist_enforced(tmp_path: Path):
    svc = RuntimeApiService(RuntimeApiConfig(root=ROOT, state_path=tmp_path / "state.json"))
    job = svc.submit_job(payload={"payload": {"x": 1}}, token="token-a", scope="jobs:write")
    try:
        svc.replay(job["job_id"], token="token-a", scope="jobs:read")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "invalid scope" in str(exc)


def test_evidence_rejects_viewer_role(tmp_path: Path):
    svc = RuntimeApiService(RuntimeApiConfig(root=ROOT, state_path=tmp_path / "state.json"))
    job = svc.submit_job(payload={"payload": {"x": 1}}, token="token-a", scope="jobs:write")
    try:
        svc.evidence(job["job_id"], token="role:viewer", scope="evidence:read")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "unauthorized action" in str(exc)


def test_replay_rejects_auditor_role(tmp_path: Path):
    svc = RuntimeApiService(RuntimeApiConfig(root=ROOT, state_path=tmp_path / "state.json"))
    job = svc.submit_job(payload={"payload": {"x": 1}}, token="token-a", scope="jobs:write")
    try:
        svc.replay(job["job_id"], token="role:auditor", scope="replay:run")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "unauthorized action" in str(exc)


def test_token_request_quota_enforced(tmp_path: Path):
    svc = RuntimeApiService(
        RuntimeApiConfig(
            root=ROOT,
            state_path=tmp_path / "state.json",
            max_requests_per_token=3,
            max_submits_per_token=3,
            max_reads_per_job=10,
        )
    )
    payload = {"payload": {"job": "demo"}}
    job = svc.submit_job(payload=payload, token="token-a", scope="jobs:write")
    svc.status(job["job_id"], token="token-a", scope="jobs:read")
    svc.status(job["job_id"], token="token-a", scope="jobs:read")
    try:
        svc.status(job["job_id"], token="token-a", scope="jobs:read")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "token request quota exceeded" in str(exc)


def test_token_burst_rate_limit_enforced(tmp_path: Path):
    svc = RuntimeApiService(
        RuntimeApiConfig(
            root=ROOT,
            state_path=tmp_path / "state.json",
            max_requests_per_token=100,
            max_submits_per_token=100,
            max_requests_per_window=2,
            request_window_seconds=60,
        )
    )
    payload = {"payload": {"job": "demo"}}
    svc.submit_job(payload=payload, token="token-burst", scope="jobs:write")
    svc.submit_job(payload=payload, token="token-burst", scope="jobs:write")
    try:
        svc.submit_job(payload=payload, token="token-burst", scope="jobs:write")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "token burst rate exceeded" in str(exc)


def test_job_read_quota_enforced(tmp_path: Path):
    svc = RuntimeApiService(
        RuntimeApiConfig(
            root=ROOT,
            state_path=tmp_path / "state.json",
            max_requests_per_token=10,
            max_submits_per_token=10,
            max_reads_per_job=2,
        )
    )
    payload = {"payload": {"job": "demo"}}
    job = svc.submit_job(payload=payload, token="token-a", scope="jobs:write")
    svc.status(job["job_id"], token="token-a", scope="jobs:read")
    svc.status(job["job_id"], token="token-a", scope="jobs:read")
    try:
        svc.status(job["job_id"], token="token-a", scope="jobs:read")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "job read quota exceeded" in str(exc)


def test_replay_quota_enforced(tmp_path: Path):
    root = tmp_path / "repo"
    (root / "evidence" / "conformance" / "reports").mkdir(parents=True)
    (root / "artifacts" / "bundles").mkdir(parents=True)
    (root / "evidence" / "repro").mkdir(parents=True)
    (root / "evidence" / "conformance" / "reports" / "latest.json").write_text(
        json.dumps({"status": "PASS"}) + "\n", encoding="utf-8"
    )
    line = "abc123  hello-core-bundle.tar.gz\n"
    (root / "artifacts" / "bundles" / "hello-core-bundle.sha256").write_text(line, encoding="utf-8")
    (root / "evidence" / "repro" / "hashes.txt").write_text(line, encoding="utf-8")

    svc = RuntimeApiService(
        RuntimeApiConfig(
            root=root,
            state_path=tmp_path / "state.json",
            max_replays_per_job=1,
            replay_cooldown_seconds=0,
        )
    )
    job = svc.submit_job(payload={"payload": {"n": 1}}, token="token-a", scope="jobs:write")
    svc.replay(job["job_id"], token="token-a", scope="replay:run")
    try:
        svc.replay(job["job_id"], token="token-a", scope="replay:run")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "job replay quota exceeded" in str(exc)


def test_replay_cooldown_enforced(tmp_path: Path):
    root = tmp_path / "repo"
    (root / "evidence" / "conformance" / "reports").mkdir(parents=True)
    (root / "artifacts" / "bundles").mkdir(parents=True)
    (root / "evidence" / "repro").mkdir(parents=True)
    (root / "evidence" / "conformance" / "reports" / "latest.json").write_text(
        json.dumps({"status": "PASS"}) + "\n", encoding="utf-8"
    )
    line = "abc123  hello-core-bundle.tar.gz\n"
    (root / "artifacts" / "bundles" / "hello-core-bundle.sha256").write_text(line, encoding="utf-8")
    (root / "evidence" / "repro" / "hashes.txt").write_text(line, encoding="utf-8")

    svc = RuntimeApiService(
        RuntimeApiConfig(
            root=root,
            state_path=tmp_path / "state.json",
            max_replays_per_job=10,
            replay_cooldown_seconds=60,
        )
    )
    job = svc.submit_job(payload={"payload": {"n": 1}}, token="token-a", scope="jobs:write")
    svc.replay(job["job_id"], token="token-a", scope="replay:run")
    try:
        svc.replay(job["job_id"], token="token-a", scope="replay:run")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "replay cooldown active" in str(exc)


def test_replay_window_limits_enforced(tmp_path: Path):
    root = tmp_path / "repo"
    (root / "evidence" / "conformance" / "reports").mkdir(parents=True)
    (root / "artifacts" / "bundles").mkdir(parents=True)
    (root / "evidence" / "repro").mkdir(parents=True)
    (root / "evidence" / "conformance" / "reports" / "latest.json").write_text(
        json.dumps({"status": "PASS"}) + "\n", encoding="utf-8"
    )
    line = "abc123  hello-core-bundle.tar.gz\n"
    (root / "artifacts" / "bundles" / "hello-core-bundle.sha256").write_text(line, encoding="utf-8")
    (root / "evidence" / "repro" / "hashes.txt").write_text(line, encoding="utf-8")

    svc = RuntimeApiService(
        RuntimeApiConfig(
            root=root,
            state_path=tmp_path / "state.json",
            max_replays_per_job=100,
            replay_cooldown_seconds=0,
            max_replays_per_token_window=2,
            max_replays_per_job_window=2,
            replay_window_seconds=60,
        )
    )
    job = svc.submit_job(payload={"payload": {"n": 1}}, token="token-window", scope="jobs:write")
    svc.replay(job["job_id"], token="token-window", scope="replay:run")
    svc.replay(job["job_id"], token="token-window", scope="replay:run")
    try:
        svc.replay(job["job_id"], token="token-window", scope="replay:run")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "replay burst exceeded" in str(exc)


def test_cross_token_replay_window_limit_enforced(tmp_path: Path):
    root = tmp_path / "repo"
    (root / "evidence" / "conformance" / "reports").mkdir(parents=True)
    (root / "artifacts" / "bundles").mkdir(parents=True)
    (root / "evidence" / "repro").mkdir(parents=True)
    (root / "evidence" / "conformance" / "reports" / "latest.json").write_text(
        json.dumps({"status": "PASS"}) + "\n", encoding="utf-8"
    )
    line = "abc123  hello-core-bundle.tar.gz\n"
    (root / "artifacts" / "bundles" / "hello-core-bundle.sha256").write_text(line, encoding="utf-8")
    (root / "evidence" / "repro" / "hashes.txt").write_text(line, encoding="utf-8")
    svc = RuntimeApiService(
        RuntimeApiConfig(
            root=root,
            state_path=tmp_path / "state.json",
            replay_cooldown_seconds=0,
            max_cross_token_replays_per_job_window=2,
            replay_window_seconds=300,
        )
    )
    job = svc.submit_job(payload={"payload": {"n": 1}}, token="alpha-token-123", scope="jobs:write")
    svc.replay(job["job_id"], token="alpha-token-123", scope="replay:run")
    svc.replay(job["job_id"], token="beta-token-456", scope="replay:run")
    try:
        svc.replay(job["job_id"], token="gamma-token-789", scope="replay:run")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "cross-token replay burst exceeded" in str(exc)


def test_auth_failure_denylist_cooldown_enforced(tmp_path: Path):
    svc = RuntimeApiService(
        RuntimeApiConfig(
            root=ROOT,
            state_path=tmp_path / "state.json",
            auth_failure_denylist_threshold=2,
            auth_failure_denylist_cooldown_seconds=3600,
        )
    )
    for _ in range(2):
        try:
            svc.submit_job(payload={"payload": {"x": 1}}, token="role:viewer", scope="jobs:write")
            assert False, "expected ValueError"
        except ValueError:
            pass
    try:
        svc.submit_job(payload={"payload": {"x": 1}}, token="role:viewer", scope="jobs:write")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "temporarily denied" in str(exc)


def test_quota_counters_stress_under_multithreaded_submissions(tmp_path: Path):
    token = "token-stress-123456"
    max_requests = 12
    attempts = 40
    svc = RuntimeApiService(
        RuntimeApiConfig(
            root=ROOT,
            state_path=tmp_path / "state.json",
            max_requests_per_token=max_requests,
            max_submits_per_token=10_000,
            max_requests_per_window=0,
            request_window_seconds=0,
        )
    )

    def _submit(ix: int) -> str:
        try:
            svc.submit_job(payload={"payload": {"ix": ix}}, token=token, scope="jobs:write")
            return "ok"
        except ValueError as exc:
            return str(exc)

    with ThreadPoolExecutor(max_workers=10) as pool:
        outcomes = list(pool.map(_submit, range(attempts)))

    success = sum(1 for item in outcomes if item == "ok")
    failures = [item for item in outcomes if item != "ok"]
    assert success == max_requests
    assert len(failures) == attempts - max_requests
    assert all("token request quota exceeded" in item for item in failures)

    state = json.loads((tmp_path / "state.json").read_text(encoding="utf-8"))
    assert state["quotas"]["token_requests"][token] == max_requests


def test_abuse_counters_stress_under_multithreaded_auth_failures(tmp_path: Path):
    token = "role:viewer"
    threshold = 5
    attempts = 30
    svc = RuntimeApiService(
        RuntimeApiConfig(
            root=ROOT,
            state_path=tmp_path / "state.json",
            auth_failure_denylist_threshold=threshold,
            auth_failure_denylist_cooldown_seconds=3600,
        )
    )

    def _submit_fail(_ix: int) -> str:
        try:
            svc.submit_job(payload={"payload": {"x": 1}}, token=token, scope="jobs:write")
            return "unexpected_success"
        except ValueError as exc:
            return str(exc)

    with ThreadPoolExecutor(max_workers=8) as pool:
        outcomes = list(pool.map(_submit_fail, range(attempts)))

    assert all(item != "unexpected_success" for item in outcomes)
    state = json.loads((tmp_path / "state.json").read_text(encoding="utf-8"))
    failures = int(state["quotas"]["auth_failures_by_token"].get(token, 0))
    assert failures >= attempts
    until = int(state["quotas"]["auth_failure_cooldown_until"].get(token, 0))
    assert until > 0


def test_token_policy_entropy_validation_enforced_in_non_test_env(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("GLYPHSER_ENV", "ci")
    svc = RuntimeApiService(
        RuntimeApiConfig(
            root=ROOT,
            state_path=tmp_path / "state.json",
            min_token_entropy_bits=80,
            enforce_token_policy=True,
        )
    )
    try:
        svc.submit_job(payload={"payload": {"x": 1}}, token="aaaaaaaaaaaaaaaa", scope="jobs:write")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "entropy" in str(exc)


def test_idempotency_ttl_prunes_and_refreshes_meta(tmp_path: Path):
    svc = RuntimeApiService(
        RuntimeApiConfig(
            root=ROOT,
            state_path=tmp_path / "state.json",
            idempotency_ttl_seconds=1,
            idempotency_max_entries=100,
        )
    )
    payload = {"payload": {"job": "demo", "value": 1}}
    _ = svc.submit_job(payload=payload, token="entropy-token-12345", scope="jobs:write", idempotency_key="ttl-key")
    state = json.loads((tmp_path / "state.json").read_text(encoding="utf-8"))
    state["idempotency_meta"]["ttl-key"]["ts"] = 0
    (tmp_path / "state.json").write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _ = svc.submit_job(payload=payload, token="entropy-token-12345", scope="jobs:write", idempotency_key="ttl-key")
    state2 = json.loads((tmp_path / "state.json").read_text(encoding="utf-8"))
    assert int(state2["idempotency_meta"]["ttl-key"]["ts"]) > 0


def test_emergency_lockdown_blocks_publish_and_replay(tmp_path: Path):
    root = tmp_path / "repo"
    (root / "governance" / "security").mkdir(parents=True)
    (root / "governance" / "security" / "emergency_lockdown_policy.json").write_text(
        json.dumps(
            {
                "lockdown_enabled": True,
                "disable_publish": True,
                "disable_replay": True,
                "reason": "incident",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    svc = RuntimeApiService(RuntimeApiConfig(root=root, state_path=tmp_path / "state.json"))
    try:
        svc.submit_job(payload={"payload": {"x": 1}}, token="token-long-123", scope="jobs:write")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "emergency lockdown" in str(exc)


def test_endpoint_specific_request_size_limit_enforced(tmp_path: Path):
    svc = RuntimeApiService(
        RuntimeApiConfig(
            root=ROOT,
            state_path=tmp_path / "state.json",
            submit_request_max_bytes=64,
        )
    )
    payload = {"payload": {"blob": "x" * 256}}
    try:
        svc.submit_job(payload=payload, token="token-size-123", scope="jobs:write")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "submit request too large" in str(exc)


def test_job_read_window_limit_enforced(tmp_path: Path):
    svc = RuntimeApiService(
        RuntimeApiConfig(
            root=ROOT,
            state_path=tmp_path / "state.json",
            max_requests_per_token=100,
            max_submits_per_token=100,
            max_reads_per_job=100,
            max_job_reads_per_window=2,
            job_read_window_seconds=60,
        )
    )
    job = svc.submit_job(payload={"payload": {"job": "demo"}}, token="token-job-read", scope="jobs:write")
    svc.status(job["job_id"], token="token-job-read", scope="jobs:read")
    svc.status(job["job_id"], token="token-job-read", scope="jobs:read")
    try:
        svc.status(job["job_id"], token="token-job-read", scope="jobs:read")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "job read burst exceeded" in str(exc)


def test_replay_token_binding_lifecycle_enforced(tmp_path: Path):
    root = tmp_path / "repo"
    (root / "evidence" / "conformance" / "reports").mkdir(parents=True)
    (root / "artifacts" / "bundles").mkdir(parents=True)
    (root / "evidence" / "repro").mkdir(parents=True)
    (root / "evidence" / "conformance" / "reports" / "latest.json").write_text(
        json.dumps({"status": "PASS"}) + "\n", encoding="utf-8"
    )
    line = "abc123  hello-core-bundle.tar.gz\n"
    (root / "artifacts" / "bundles" / "hello-core-bundle.sha256").write_text(line, encoding="utf-8")
    (root / "evidence" / "repro" / "hashes.txt").write_text(line, encoding="utf-8")

    svc = RuntimeApiService(
        RuntimeApiConfig(
            root=root,
            state_path=tmp_path / "state.json",
            enforce_replay_token_binding=True,
            replay_token_ttl_seconds=3600,
            replay_token_max_uses=1,
            replay_cooldown_seconds=0,
        )
    )
    job = svc.submit_job(payload={"payload": {"n": 1}}, token="bound-token-1", scope="jobs:write")

    try:
        svc.replay(job["job_id"], token="bound-token-2", scope="replay:run")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "binding mismatch" in str(exc)

    _ = svc.replay(job["job_id"], token="bound-token-1", scope="replay:run")
    try:
        svc.replay(job["job_id"], token="bound-token-1", scope="replay:run")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "use limit exceeded" in str(exc)


def test_replay_failure_reason_hidden_by_default(tmp_path: Path):
    root = tmp_path / "repo"
    (root / "evidence" / "conformance" / "reports").mkdir(parents=True)
    (root / "artifacts" / "bundles").mkdir(parents=True)
    (root / "evidence" / "conformance" / "reports" / "latest.json").write_text(
        json.dumps({"status": "PASS"}) + "\n", encoding="utf-8"
    )
    (root / "artifacts" / "bundles" / "hello-core-bundle.sha256").write_text(
        "abc123  hello-core-bundle.tar.gz\n", encoding="utf-8"
    )
    svc = RuntimeApiService(RuntimeApiConfig(root=root, state_path=tmp_path / "state.json", replay_cooldown_seconds=0))
    job = svc.submit_job(payload={"payload": {"n": 1}}, token="token-reason", scope="jobs:write")
    out = svc.replay(job["job_id"], token="token-reason", scope="replay:run")
    assert out["replay_verdict"] == "FAIL"
    assert "reason" not in out


def test_signed_token_auth_succeeds_when_valid(monkeypatch, tmp_path: Path):
    key = "runtime-api-test-secret"
    monkeypatch.setenv("GLYPHSER_RUNTIME_API_TOKEN_HMAC_KEY", key)
    svc = RuntimeApiService(
        RuntimeApiConfig(
            root=ROOT,
            state_path=tmp_path / "state.json",
            enforce_signed_tokens=True,
        )
    )
    token = _signed_token(key=key, scope="jobs:write", aud="glyphser-runtime-api:jobs:write", jti="signed-ok")
    out = svc.submit_job(payload={"payload": {"x": 1}}, token=token, scope="jobs:write")
    assert out["status"] == "accepted"


def test_signed_token_rejected_when_expired(monkeypatch, tmp_path: Path):
    key = "runtime-api-test-secret"
    monkeypatch.setenv("GLYPHSER_RUNTIME_API_TOKEN_HMAC_KEY", key)
    svc = RuntimeApiService(
        RuntimeApiConfig(
            root=ROOT,
            state_path=tmp_path / "state.json",
            enforce_signed_tokens=True,
            token_clock_skew_seconds=0,
        )
    )
    token = _signed_token(
        key=key,
        scope="jobs:write",
        aud="glyphser-runtime-api:jobs:write",
        exp=int(time.time()) - 1,
        jti="signed-expired",
    )
    try:
        svc.submit_job(payload={"payload": {"x": 1}}, token=token, scope="jobs:write")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "expired" in str(exc)


def test_signed_token_rejected_on_audience_mismatch(monkeypatch, tmp_path: Path):
    key = "runtime-api-test-secret"
    monkeypatch.setenv("GLYPHSER_RUNTIME_API_TOKEN_HMAC_KEY", key)
    svc = RuntimeApiService(
        RuntimeApiConfig(
            root=ROOT,
            state_path=tmp_path / "state.json",
            enforce_signed_tokens=True,
        )
    )
    token = _signed_token(key=key, scope="jobs:write", aud="glyphser-runtime-api:jobs:read", jti="signed-bad-aud")
    try:
        svc.submit_job(payload={"payload": {"x": 1}}, token=token, scope="jobs:write")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "audience invalid" in str(exc)


def test_signed_token_jti_replay_protection(monkeypatch, tmp_path: Path):
    key = "runtime-api-test-secret"
    monkeypatch.setenv("GLYPHSER_RUNTIME_API_TOKEN_HMAC_KEY", key)
    svc = RuntimeApiService(
        RuntimeApiConfig(
            root=ROOT,
            state_path=tmp_path / "state.json",
            enforce_signed_tokens=True,
            enforce_token_jti_replay_protection=True,
        )
    )
    token = _signed_token(key=key, scope="jobs:write", aud="glyphser-runtime-api:jobs:write", jti="reused-jti")
    _ = svc.submit_job(payload={"payload": {"x": 1}}, token=token, scope="jobs:write")
    try:
        svc.submit_job(payload={"payload": {"x": 2}}, token=token, scope="jobs:write")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "jti replay" in str(exc)
