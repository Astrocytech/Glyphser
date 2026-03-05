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

REGISTRY = ROOT / "governance" / "security" / "ownership_registry.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _collect_targets() -> tuple[list[str], list[str], list[str]]:
    policies = [str(p.relative_to(ROOT)).replace("\\", "/") for p in sorted((ROOT / "governance" / "security").glob("*.json"))]
    gates = [str(p.relative_to(ROOT)).replace("\\", "/") for p in sorted((ROOT / "tooling" / "security").glob("*_gate.py"))]
    workflows = [str(p.relative_to(ROOT)).replace("\\", "/") for p in sorted((ROOT / ".github" / "workflows").glob("*.yml"))]
    return policies, gates, workflows


def _resolve_owner(path: str, default_owner: str, overrides: dict[str, str]) -> str:
    return str(overrides.get(path, default_owner)).strip()


def _resolve_owner_with_fallback(
    path: str,
    *,
    default_owner: str,
    default_fallback_owner: str,
    owner_overrides: dict[str, str],
    fallback_overrides: dict[str, str],
) -> tuple[str, str]:
    primary = _resolve_owner(path, default_owner, owner_overrides)
    fallback = _resolve_owner(path, default_fallback_owner, fallback_overrides)
    return primary, fallback


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not REGISTRY.exists():
        findings.append("missing_ownership_registry")
        registry = {}
    else:
        try:
            registry = _load_json(REGISTRY)
        except Exception:
            registry = {}
            findings.append("invalid_ownership_registry")

    default_policy_owner = str(registry.get("default_policy_owner", "")).strip()
    default_gate_owner = str(registry.get("default_gate_owner", "")).strip()
    default_workflow_owner = str(registry.get("default_workflow_owner", "")).strip()
    default_policy_fallback_owner = str(registry.get("default_policy_fallback_owner", "")).strip()
    default_gate_fallback_owner = str(registry.get("default_gate_fallback_owner", "")).strip()
    default_workflow_fallback_owner = str(registry.get("default_workflow_fallback_owner", "")).strip()

    policy_overrides = registry.get("policy_owners", {}) if isinstance(registry, dict) else {}
    gate_overrides = registry.get("gate_owners", {}) if isinstance(registry, dict) else {}
    workflow_overrides = registry.get("workflow_owners", {}) if isinstance(registry, dict) else {}
    policy_fallback_overrides = registry.get("policy_fallback_owners", {}) if isinstance(registry, dict) else {}
    gate_fallback_overrides = registry.get("gate_fallback_owners", {}) if isinstance(registry, dict) else {}
    workflow_fallback_overrides = registry.get("workflow_fallback_owners", {}) if isinstance(registry, dict) else {}
    policy_overrides = {str(k): str(v) for k, v in policy_overrides.items()} if isinstance(policy_overrides, dict) else {}
    gate_overrides = {str(k): str(v) for k, v in gate_overrides.items()} if isinstance(gate_overrides, dict) else {}
    workflow_overrides = {str(k): str(v) for k, v in workflow_overrides.items()} if isinstance(workflow_overrides, dict) else {}
    policy_fallback_overrides = (
        {str(k): str(v) for k, v in policy_fallback_overrides.items()}
        if isinstance(policy_fallback_overrides, dict)
        else {}
    )
    gate_fallback_overrides = (
        {str(k): str(v) for k, v in gate_fallback_overrides.items()} if isinstance(gate_fallback_overrides, dict) else {}
    )
    workflow_fallback_overrides = (
        {str(k): str(v) for k, v in workflow_fallback_overrides.items()}
        if isinstance(workflow_fallback_overrides, dict)
        else {}
    )

    policies, gates, workflows = _collect_targets()

    for path in policies:
        primary, fallback = _resolve_owner_with_fallback(
            path,
            default_owner=default_policy_owner,
            default_fallback_owner=default_policy_fallback_owner,
            owner_overrides=policy_overrides,
            fallback_overrides=policy_fallback_overrides,
        )
        if not primary:
            findings.append(f"unowned_policy:{path}")
        if not fallback:
            findings.append(f"missing_policy_fallback_owner:{path}")
        if primary and fallback and primary == fallback:
            findings.append(f"policy_fallback_matches_primary:{path}")
    for path in gates:
        primary, fallback = _resolve_owner_with_fallback(
            path,
            default_owner=default_gate_owner,
            default_fallback_owner=default_gate_fallback_owner,
            owner_overrides=gate_overrides,
            fallback_overrides=gate_fallback_overrides,
        )
        if not primary:
            findings.append(f"unowned_gate:{path}")
        if not fallback:
            findings.append(f"missing_gate_fallback_owner:{path}")
        if primary and fallback and primary == fallback:
            findings.append(f"gate_fallback_matches_primary:{path}")
    for path in workflows:
        primary, fallback = _resolve_owner_with_fallback(
            path,
            default_owner=default_workflow_owner,
            default_fallback_owner=default_workflow_fallback_owner,
            owner_overrides=workflow_overrides,
            fallback_overrides=workflow_fallback_overrides,
        )
        if not primary:
            findings.append(f"unowned_workflow:{path}")
        if not fallback:
            findings.append(f"missing_workflow_fallback_owner:{path}")
        if primary and fallback and primary == fallback:
            findings.append(f"workflow_fallback_matches_primary:{path}")

    existing = set(policies) | set(gates) | set(workflows)
    for path in sorted(
        set(policy_overrides)
        | set(gate_overrides)
        | set(workflow_overrides)
        | set(policy_fallback_overrides)
        | set(gate_fallback_overrides)
        | set(workflow_fallback_overrides)
    ):
        if path not in existing:
            findings.append(f"ownership_override_missing_target:{path}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "policies_checked": len(policies),
            "gates_checked": len(gates),
            "workflows_checked": len(workflows),
        },
        "metadata": {"gate": "ownership_continuity_gate"},
    }
    out = evidence_root() / "security" / "ownership_continuity_gate.json"
    write_json_report(out, report)
    print(f"OWNERSHIP_CONTINUITY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
