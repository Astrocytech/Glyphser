from __future__ import annotations

import json
from pathlib import Path

from src.glyphser.api.runtime_api import RuntimeApiConfig, RuntimeApiService


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
    (root / "evidence" / "conformance" / "reports" / "latest.json").write_text(json.dumps({"status": "PASS"}) + "\n", encoding="utf-8")
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
