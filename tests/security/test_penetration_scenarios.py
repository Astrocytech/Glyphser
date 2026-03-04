from __future__ import annotations

import json
from pathlib import Path

import pytest

from runtime.glyphser.api.runtime_api import RuntimeApiConfig, RuntimeApiService
from runtime.glyphser.checkpoint.restore import restore_checkpoint


def _prep(root: Path) -> RuntimeApiService:
    (root / "evidence" / "conformance" / "reports").mkdir(parents=True)
    (root / "artifacts" / "bundles").mkdir(parents=True)
    (root / "evidence" / "repro").mkdir(parents=True)
    (root / "evidence" / "conformance" / "reports" / "latest.json").write_text(
        json.dumps({"status": "PASS"}) + "\n", encoding="utf-8"
    )
    line = "abc123  hello-core-bundle.tar.gz\n"
    (root / "artifacts" / "bundles" / "hello-core-bundle.sha256").write_text(line, encoding="utf-8")
    (root / "evidence" / "repro" / "hashes.txt").write_text(line, encoding="utf-8")
    return RuntimeApiService(RuntimeApiConfig(root=root, state_path=root / "state.json"))


def test_penetration_authz_scope_escalation_blocked(tmp_path: Path) -> None:
    svc = _prep(tmp_path / "repo")
    with pytest.raises(ValueError, match="invalid scope"):
        svc.submit_job(payload={"payload": {"x": 1}}, token="role:operator", scope="security:admin")


def test_penetration_payload_key_injection_blocked(tmp_path: Path) -> None:
    svc = _prep(tmp_path / "repo")
    with pytest.raises(ValueError, match="payload key not allowed"):
        svc.submit_job(payload={"bad key": {"x": 1}}, token="role:operator", scope="jobs:write")


def test_penetration_checkpoint_traversal_blocked(tmp_path: Path) -> None:
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    outside = tmp_path / "outside.json"
    outside.write_text('{"x":1}\n', encoding="utf-8")
    with pytest.raises(ValueError, match="path escapes allowed root"):
        restore_checkpoint({"path": str(outside), "allowed_root": str(allowed)})
