from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "tooling" / "cli" / "api_cli.py"


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(CLI), *args], cwd=ROOT, check=False, text=True, capture_output=True)


def test_api_cli_submit_status_evidence_replay(tmp_path: Path):
    state = tmp_path / "state.json"
    payload = tmp_path / "payload.json"
    payload.write_text(json.dumps({"payload": {"x": 1}}), encoding="utf-8")

    submit = _run(
        "--state-path", str(state),
        "submit",
        "--payload-file", str(payload),
        "--token", "token-a",
        "--scope", "jobs:write",
        "--idempotency-key", "k1",
    )
    assert submit.returncode == 0
    submitted = json.loads(submit.stdout)
    job_id = submitted["job_id"]

    status = _run("--state-path", str(state), "status", "--job-id", job_id, "--token", "token-a", "--scope", "jobs:read")
    assert status.returncode == 0
    assert json.loads(status.stdout)["job_id"] == job_id

    evidence = _run("--state-path", str(state), "evidence", "--job-id", job_id, "--token", "token-a", "--scope", "evidence:read")
    assert evidence.returncode == 0
    assert "job_id" in json.loads(evidence.stdout)

    replay = _run("--state-path", str(state), "replay", "--job-id", job_id, "--token", "token-a", "--scope", "replay:run")
    assert replay.returncode == 0
    assert json.loads(replay.stdout)["job_id"] == job_id

