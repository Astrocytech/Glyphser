from __future__ import annotations

import json
from pathlib import Path

from tooling.security import release_publish_artifact_presence_gate


def _write(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def _create_required_artifacts(root: Path, run_id: str) -> Path:
    sec = root / "evidence" / "runs" / run_id / "release-build" / "security"
    for name in release_publish_artifact_presence_gate.REQUIRED_SECURITY_ARTIFACTS:
        _write(sec / name, {"status": "PASS"})
    return sec


def test_release_publish_artifact_presence_gate_passes_when_required_artifacts_present(tmp_path: Path) -> None:
    run_id = "12345"
    sec = _create_required_artifacts(tmp_path, run_id)
    assert release_publish_artifact_presence_gate.main(["--artifact-root", str(tmp_path), "--run-id", run_id]) == 0
    payload = json.loads((sec / "release_publish_artifact_presence_gate.json").read_text(encoding="utf-8"))
    assert payload["status"] == "PASS"
    assert payload["summary"]["missing_security_artifact_count"] == 0


def test_release_publish_artifact_presence_gate_fails_when_any_required_artifact_missing(tmp_path: Path) -> None:
    run_id = "8888"
    sec = _create_required_artifacts(tmp_path, run_id)
    (sec / "policy_signature.json").unlink()
    assert release_publish_artifact_presence_gate.main(["--artifact-root", str(tmp_path), "--run-id", run_id]) == 1
    payload = json.loads((sec / "release_publish_artifact_presence_gate.json").read_text(encoding="utf-8"))
    assert payload["status"] == "FAIL"
    assert any(
        item.endswith(f"/{run_id}/release-build/security/policy_signature.json")
        for item in payload["summary"]["missing_security_artifacts"]
    )
