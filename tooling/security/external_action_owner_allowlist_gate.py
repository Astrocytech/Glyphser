#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

POLICY = ROOT / "governance" / "security" / "external_action_owner_allowlist.json"
WORKFLOWS = ROOT / ".github" / "workflows"
_ACTION_RE = re.compile(r"^\s*-?\s*uses:\s*([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)(?:/[A-Za-z0-9_.-]+)*@")


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _workflow_action_owners() -> dict[str, list[str]]:
    owners: dict[str, list[str]] = {}
    for wf in sorted(WORKFLOWS.glob("*.yml")):
        for line in wf.read_text(encoding="utf-8").splitlines():
            match = _ACTION_RE.match(line)
            if not match:
                continue
            owner = match.group(1).strip().lower()
            if owner.startswith("./"):
                continue
            owners.setdefault(owner, []).append(wf.name)
    return owners


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not POLICY.exists():
        findings.append("missing_external_action_owner_allowlist_policy")
        policy = {}
        allowed: set[str] = set()
    else:
        try:
            policy = _load_json(POLICY)
        except Exception:
            policy = {}
            findings.append("invalid_external_action_owner_allowlist_policy")

        sig_path = POLICY.with_suffix(POLICY.suffix + ".sig")
        if not sig_path.exists():
            findings.append("missing_external_action_owner_allowlist_policy_signature")
        else:
            sig = sig_path.read_text(encoding="utf-8").strip()
            key = artifact_signing.current_key(strict=False)
            if not artifact_signing.verify_file(POLICY, sig, key=key):
                findings.append("invalid_external_action_owner_allowlist_policy_signature")

        raw = policy.get("allowed_action_owners", []) if isinstance(policy, dict) else []
        allowed = {str(item).strip().lower() for item in raw if isinstance(item, str) and str(item).strip()}

    observed = _workflow_action_owners()
    observed_owners = set(observed.keys())
    disallowed = sorted(observed_owners - allowed)
    for owner in disallowed:
        workflows = sorted(set(observed.get(owner, [])))
        findings.append(f"disallowed_action_owner:{owner}:workflows:{','.join(workflows)}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "allowed_action_owners": len(allowed),
            "observed_action_owners": len(observed_owners),
            "disallowed_action_owners": len(disallowed),
        },
        "owners": {
            "allowed": sorted(allowed),
            "observed": {owner: sorted(set(files)) for owner, files in sorted(observed.items())},
            "disallowed": disallowed,
        },
        "metadata": {"gate": "external_action_owner_allowlist_gate"},
    }
    out = evidence_root() / "security" / "external_action_owner_allowlist_gate.json"
    write_json_report(out, report)
    print(f"EXTERNAL_ACTION_OWNER_ALLOWLIST_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
