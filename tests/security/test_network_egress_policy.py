from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_network_egress_policy_defaults_to_deny_with_explicit_allowlist() -> None:
    policy = json.loads((ROOT / "governance" / "security" / "network_egress_policy.json").read_text(encoding="utf-8"))
    assert policy["default_gate_network_egress"] == "deny"
    allow = policy["network_required_gates"]
    assert "tooling/security/live_integrations_verify.py" in allow
    assert "tooling/security/live_rollout_gate.py" in allow
