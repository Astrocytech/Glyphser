from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.api.runtime_api import RuntimeApiConfig, RuntimeApiService

ROOT = Path(__file__).resolve().parents[2]


def test_submit_idempotency_and_status(tmp_path: Path):
    svc = RuntimeApiService(RuntimeApiConfig(root=ROOT, state_path=tmp_path / "state.json"))
    payload = {"payload": {"job": "demo", "value": 1}}
    first = svc.submit_job(payload=payload, token="token-a", scope="jobs:write", idempotency_key="abc")
    second = svc.submit_job(payload=payload, token="token-a", scope="jobs:write", idempotency_key="abc")
    assert first["job_id"] == second["job_id"]
    status = svc.status(first["job_id"], token="token-a", scope="jobs:read")
    assert status["status"] == "accepted"
    assert status["api_version"] == "1.0.0"


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
    svc = RuntimeApiService(RuntimeApiConfig(root=ROOT, state_path=tmp_path / "state.json"))
    try:
        svc.submit_job(payload={"payload": {"x": 1}}, token="role:viewer", scope="jobs:write")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "unauthorized action" in str(exc)
    state = json.loads((tmp_path / "state.json").read_text(encoding="utf-8"))
    failures = state.get("quotas", {}).get("auth_failures_by_token", {})
    assert failures.get("role:viewer", 0) >= 1


def test_submit_rejects_payload_too_large(tmp_path: Path):
    svc = RuntimeApiService(RuntimeApiConfig(root=ROOT, state_path=tmp_path / "state.json"))
    payload = {"payload": {"blob": "x" * (130 * 1024)}}
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


def test_scope_allowlist_enforced(tmp_path: Path):
    svc = RuntimeApiService(RuntimeApiConfig(root=ROOT, state_path=tmp_path / "state.json"))
    try:
        svc.submit_job(payload={"payload": {"x": 1}}, token="token-a", scope="jobs:read")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "invalid scope" in str(exc)


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
