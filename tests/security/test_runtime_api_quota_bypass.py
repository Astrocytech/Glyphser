from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.api.runtime_api import RuntimeApiConfig, RuntimeApiService


def _prep_root(root: Path) -> None:
    (root / "evidence" / "conformance" / "reports").mkdir(parents=True)
    (root / "artifacts" / "bundles").mkdir(parents=True)
    (root / "evidence" / "repro").mkdir(parents=True)
    (root / "evidence" / "conformance" / "reports" / "latest.json").write_text(
        json.dumps({"status": "PASS"}) + "\n",
        encoding="utf-8",
    )
    line = "abc123  hello-core-bundle.tar.gz\n"
    (root / "artifacts" / "bundles" / "hello-core-bundle.sha256").write_text(line, encoding="utf-8")
    (root / "evidence" / "repro" / "hashes.txt").write_text(line, encoding="utf-8")


def test_role_token_cannot_bypass_per_token_submit_quota(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    _prep_root(root)
    svc = RuntimeApiService(
        RuntimeApiConfig(
            root=root,
            state_path=tmp_path / "state.json",
            max_requests_per_token=2,
            max_submits_per_token=2,
        )
    )
    payload = {"payload": {"n": 1}}
    svc.submit_job(payload=payload, token="role:operator", scope="jobs:write")
    svc.submit_job(payload=payload, token="role:operator", scope="jobs:write")
    try:
        svc.submit_job(payload=payload, token="role:operator", scope="jobs:write")
    except ValueError as exc:
        assert "quota exceeded" in str(exc)
    else:
        raise AssertionError("expected role token quota enforcement")


def test_cross_token_reads_cannot_bypass_per_job_read_quota(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    _prep_root(root)
    svc = RuntimeApiService(
        RuntimeApiConfig(
            root=root,
            state_path=tmp_path / "state.json",
            max_reads_per_job=1,
            max_requests_per_token=20,
        )
    )
    job = svc.submit_job(payload={"payload": {"job": "x"}}, token="role:operator", scope="jobs:write")
    svc.status(job["job_id"], token="token-a", scope="jobs:read")
    try:
        svc.status(job["job_id"], token="token-b", scope="jobs:read")
    except ValueError as exc:
        assert "job read quota exceeded" in str(exc)
    else:
        raise AssertionError("expected per-job read quota across tokens")
