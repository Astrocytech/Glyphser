from __future__ import annotations

import json
from pathlib import Path

import pytest

from runtime.glyphser.api.runtime_api import RuntimeApiConfig, RuntimeApiService
from runtime.glyphser.security.audit import append_event, verify_chain


def test_threat_model_rbac_boundary_blocks_unauthorized_write(tmp_path: Path):
    svc = RuntimeApiService(RuntimeApiConfig(root=tmp_path, state_path=tmp_path / "state.json"))

    with pytest.raises(ValueError, match="unauthorized action"):
        svc.submit_job(payload={"payload": {"x": 1}}, token="role:viewer", scope="jobs:write")


def test_threat_model_audit_chain_detects_tamper(tmp_path: Path):
    log = tmp_path / "audit.log.jsonl"
    append_event(log, {"operation": "submit", "actor": "role:operator"})
    append_event(log, {"operation": "status", "actor": "role:auditor"})
    assert verify_chain(log)["status"] == "PASS"

    lines = log.read_text(encoding="utf-8").splitlines()
    rec = json.loads(lines[1])
    rec["event"]["operation"] = "tampered"
    lines[1] = json.dumps(rec, separators=(",", ":"), sort_keys=True)
    log.write_text("\n".join(lines) + "\n", encoding="utf-8")

    assert verify_chain(log)["status"] == "FAIL"


def test_threat_model_api_actions_emit_audit_events(tmp_path: Path):
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

    audit_path = tmp_path / "audit.log.jsonl"
    svc = RuntimeApiService(RuntimeApiConfig(root=root, state_path=tmp_path / "state.json", audit_log_path=audit_path))

    job = svc.submit_job(payload={"payload": {"n": 1}}, token="role:operator", scope="jobs:write")
    svc.status(job["job_id"], token="role:auditor", scope="jobs:read")
    svc.evidence(job["job_id"], token="role:auditor", scope="evidence:read")

    assert verify_chain(audit_path)["status"] == "PASS"
    lines = audit_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) >= 3
    first = json.loads(lines[0]).get("event", {})
    assert isinstance(first, dict)
    assert "role_token" not in first
    assert isinstance(first.get("role_token_hash", ""), str) and first.get("role_token_hash")


def test_threat_model_audit_chain_fails_closed_on_partial_append(tmp_path: Path):
    log = tmp_path / "audit.log.jsonl"
    append_event(log, {"operation": "submit", "actor": "role:operator"})
    log.write_text(
        log.read_text(encoding="utf-8") + '{"event":{"operation":"status"},"prev_hash":"x"', encoding="utf-8"
    )
    result = verify_chain(log)
    assert result["status"] == "FAIL"
    assert result["reason"] == "invalid_json"


def test_threat_model_runtime_state_fails_closed_on_corrupt_state(tmp_path: Path):
    state_path = tmp_path / "state.json"
    state_path.write_text('{"jobs":', encoding="utf-8")
    svc = RuntimeApiService(RuntimeApiConfig(root=tmp_path, state_path=state_path))
    with pytest.raises(Exception):
        svc.submit_job(payload={"payload": {"x": 1}}, token="role:operator", scope="jobs:write")
