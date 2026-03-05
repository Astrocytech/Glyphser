#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

POLICY = ROOT / "governance" / "security" / "stochastic_seed_policy.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    checks: list[dict[str, Any]] = []

    if not POLICY.exists():
        findings.append("missing_stochastic_seed_policy")
        policy: dict[str, Any] = {}
    else:
        policy = _load_json(POLICY)

    required = policy.get("stochastic_simulations", [])
    require_seed_hashing = bool(policy.get("require_seed_hashing", True))
    if not isinstance(required, list):
        required = []
        findings.append("invalid_stochastic_simulations_policy_shape")

    for idx, item in enumerate(required):
        if not isinstance(item, dict):
            findings.append(f"invalid_stochastic_simulation_entry:{idx}")
            continue
        script_rel = str(item.get("script", "")).strip()
        seed_env = str(item.get("seed_env", "")).strip()
        seed_summary_field = str(item.get("seed_summary_field", "")).strip()

        if not script_rel or not seed_env or not seed_summary_field:
            findings.append(f"invalid_stochastic_simulation_policy_fields:{idx}")
            continue

        script_path = ROOT / script_rel
        if not script_path.exists():
            findings.append(f"missing_stochastic_simulation_script:{script_rel}")
            continue

        text = script_path.read_text(encoding="utf-8")
        has_seed_env = f'os.environ.get("{seed_env}"' in text
        has_seeded_rng = "random.Random(" in text
        has_seed_summary = f'"{seed_summary_field}"' in text
        has_seed_hashing = "hashlib.sha256" in text

        checks.append(
            {
                "script": script_rel,
                "seed_env": seed_env,
                "seed_summary_field": seed_summary_field,
                "has_seed_env": has_seed_env,
                "has_seeded_rng": has_seeded_rng,
                "has_seed_summary": has_seed_summary,
                "has_seed_hashing": has_seed_hashing,
            }
        )

        if not has_seed_env:
            findings.append(f"missing_seed_env_binding:{script_rel}:{seed_env}")
        if not has_seeded_rng:
            findings.append(f"missing_seeded_rng_usage:{script_rel}")
        if not has_seed_summary:
            findings.append(f"missing_seed_summary_field:{script_rel}:{seed_summary_field}")
        if require_seed_hashing and not has_seed_hashing:
            findings.append(f"missing_seed_hashing:{script_rel}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "policy_path": str(POLICY),
            "stochastic_simulations_checked": len(checks),
            "require_seed_hashing": require_seed_hashing,
        },
        "metadata": {"gate": "stochastic_seed_policy_gate"},
        "checks": checks,
    }

    out = evidence_root() / "security" / "stochastic_seed_policy_gate.json"
    write_json_report(out, report)
    print(f"STOCHASTIC_SEED_POLICY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
