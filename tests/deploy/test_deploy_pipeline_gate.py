from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_deploy_pipeline_gate_passes():
    proc = subprocess.run(
        [sys.executable, "tools/deploy/run_deployment_pipeline.py"],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    latest = json.loads((ROOT / "evidence" / "deploy" / "latest.json").read_text(encoding="utf-8"))
    assert latest["status"] == "PASS"
    assert latest["health"]["status"] == "PASS"
    assert latest["readiness"]["status"] == "PASS"
    assert latest["rollback"]["status"] == "PASS"
