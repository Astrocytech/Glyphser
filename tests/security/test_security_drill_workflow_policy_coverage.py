from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_drill_workflows_are_covered_by_policy() -> None:
    payload = json.loads((ROOT / "governance" / "security" / "workflow_policy_coverage.json").read_text("utf-8"))
    workflows = payload.get("workflows", [])
    assert "security-compromised-runner-drill.yml" in workflows
    assert "security-replay-abuse-regression.yml" in workflows
