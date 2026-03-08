from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from runtime.glyphser.api.runtime_api import RuntimeApiConfig, RuntimeApiService
from runtime.glyphser.security.audit import append_event, verify_chain


def _prep_root(root: Path) -> None:
    (root / "evidence" / "conformance" / "reports").mkdir(parents=True)
    (root / "artifacts" / "bundles").mkdir(parents=True)
    (root / "evidence" / "repro").mkdir(parents=True)
    (root / "evidence" / "conformance" / "reports" / "latest.json").write_text(
        json.dumps({"status": "PASS"}) + "\n", encoding="utf-8"
    )
    line = "abc123  hello-core-bundle.tar.gz\n"
    (root / "artifacts" / "bundles" / "hello-core-bundle.sha256").write_text(line, encoding="utf-8")
    (root / "evidence" / "repro" / "hashes.txt").write_text(line, encoding="utf-8")


def test_replay_cooldown_under_concurrency(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    _prep_root(root)
    svc = RuntimeApiService(
        RuntimeApiConfig(
            root=root,
            state_path=tmp_path / "state.json",
            max_replays_per_job=20,
            replay_cooldown_seconds=60,
        )
    )
    job = svc.submit_job(payload={"payload": {"n": 1}}, token="token-a", scope="jobs:write")

    def _run() -> str:
        try:
            svc.replay(job["job_id"], token="token-a", scope="replay:run")
            return "ok"
        except ValueError as exc:
            return str(exc)

    with ThreadPoolExecutor(max_workers=8) as ex:
        outcomes = list(ex.map(lambda _: _run(), range(8)))
    assert outcomes.count("ok") == 1
    assert sum("replay cooldown active" in s for s in outcomes) >= 7


def test_audit_chain_survives_concurrent_appends(tmp_path: Path) -> None:
    path = tmp_path / "audit.log.jsonl"

    def _emit(ix: int) -> None:
        append_event(path, {"op": "replay", "ix": ix})

    with ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(_emit, range(100)))
    result = verify_chain(path)
    assert result["status"] == "PASS"


def test_token_spray_hits_per_token_quota(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    _prep_root(root)
    svc = RuntimeApiService(
        RuntimeApiConfig(
            root=root,
            state_path=tmp_path / "state.json",
            max_requests_per_token=3,
            max_submits_per_token=3,
        )
    )
    payload = {"payload": {"job": "spray"}}
    tokens = [f"token-{ix}" for ix in range(5)]
    for token in tokens:
        svc.submit_job(payload=payload, token=token, scope="jobs:write")
        svc.submit_job(payload=payload, token=token, scope="jobs:write")
        svc.submit_job(payload=payload, token=token, scope="jobs:write")
        try:
            svc.submit_job(payload=payload, token=token, scope="jobs:write")
            assert False, "expected token quota error"
        except ValueError as exc:
            assert "token request quota exceeded" in str(exc)


def test_concurrent_idempotency_stays_single_job(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    _prep_root(root)
    svc = RuntimeApiService(RuntimeApiConfig(root=root, state_path=tmp_path / "state.json"))
    idem = "idem-abuse-key"

    def _submit(ix: int) -> str:
        record = svc.submit_job(
            payload={"payload": {"ix": ix % 2}},
            token="token-abuse",
            scope="jobs:write",
            idempotency_key=idem,
        )
        return str(record["job_id"])

    with ThreadPoolExecutor(max_workers=12) as ex:
        ids = list(ex.map(_submit, range(60)))
    assert len(set(ids)) == 1
