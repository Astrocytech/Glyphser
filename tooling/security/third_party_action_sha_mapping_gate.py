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

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

POLICY = ROOT / "governance" / "security" / "third_party_action_commit_map.json"
WORKFLOWS = ROOT / ".github" / "workflows"
_ACTION_RE = re.compile(r"^\s*-?\s*uses:\s*([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*)@([^\s]+)")
_SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _observed_actions() -> dict[str, dict[str, Any]]:
    observed: dict[str, dict[str, Any]] = {}
    for wf in sorted(WORKFLOWS.glob("*.yml")):
        for line in wf.read_text(encoding="utf-8").splitlines():
            m = _ACTION_RE.match(line)
            if not m:
                continue
            action = m.group(1).strip().lower()
            ref = m.group(2).strip()
            entry = observed.setdefault(action, {"refs": set(), "workflows": set()})
            entry["refs"].add(ref)
            entry["workflows"].add(wf.name)
    return observed


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    expected_provenance: dict[str, str] = {}

    if not POLICY.exists():
        findings.append("missing_third_party_action_commit_map_policy")
        expected: dict[str, str] = {}
    else:
        try:
            policy = _load_json(POLICY)
        except Exception:
            policy = {}
            findings.append("invalid_third_party_action_commit_map_policy")
        raw = policy.get("expected_action_refs", {}) if isinstance(policy, dict) else {}
        expected = {str(k).strip().lower(): str(v).strip() for k, v in raw.items()} if isinstance(raw, dict) else {}
        raw_prov = policy.get("expected_action_provenance_urls", {}) if isinstance(policy, dict) else {}
        expected_provenance = (
            {str(k).strip().lower(): str(v).strip() for k, v in raw_prov.items()} if isinstance(raw_prov, dict) else {}
        )

    observed = _observed_actions()

    for action, data in sorted(observed.items()):
        refs = sorted(str(x) for x in data.get("refs", set()))
        workflows = sorted(str(x) for x in data.get("workflows", set()))
        for ref in refs:
            if not _SHA_RE.fullmatch(ref):
                findings.append(f"action_not_sha_pinned:{action}@{ref}")

        if action not in expected:
            findings.append(f"missing_expected_action_ref:{action}")
            continue

        expected_ref = expected[action]
        if expected_ref not in refs:
            findings.append(
                f"action_sha_mapping_drift:{action}:expected:{expected_ref}:observed:{','.join(refs)}:workflows:{','.join(workflows)}"
            )

        provenance_url = expected_provenance.get(action, "")
        if not provenance_url:
            findings.append(f"missing_action_provenance_url:{action}")
        else:
            parts = action.split("/")
            repo_root = "/".join(parts[:2]) if len(parts) >= 2 else action
            expected_prefix = f"https://github.com/{repo_root}"
            if not provenance_url.lower().startswith(expected_prefix.lower()):
                findings.append(f"action_provenance_url_mismatch:{action}:{provenance_url}")

    for action in sorted(set(expected.keys()) - set(observed.keys())):
        findings.append(f"policy_has_unobserved_action:{action}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "observed_actions": len(observed),
            "policy_actions": len(expected),
            "provenance_urls": len(expected_provenance),
        },
        "observed": {
            action: {
                "refs": sorted(str(x) for x in data.get("refs", set())),
                "workflows": sorted(str(x) for x in data.get("workflows", set())),
            }
            for action, data in sorted(observed.items())
        },
        "metadata": {"gate": "third_party_action_sha_mapping_gate"},
    }
    out = evidence_root() / "security" / "third_party_action_sha_mapping_gate.json"
    write_json_report(out, report)
    print(f"THIRD_PARTY_ACTION_SHA_MAPPING_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
