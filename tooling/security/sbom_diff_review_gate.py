#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, verify_file
from tooling.lib.path_config import evidence_root
from tooling.security.advanced_policy import load_policy


def _packages(path: Path) -> set[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    pkgs = payload.get("packages", []) if isinstance(payload, dict) else []
    out: set[str] = set()
    if isinstance(pkgs, list):
        for entry in pkgs:
            if isinstance(entry, dict):
                name = str(entry.get("name", "")).strip()
                version = str(entry.get("version", "")).strip()
                if name:
                    out.add(f"{name}=={version}")
    return out

ROOT = Path(__file__).resolve().parents[2]



def main(argv: list[str] | None = None) -> int:
    _ = argv
    policy = load_policy()
    cur = ROOT / str(policy.get("sbom_current_path", "evidence/security/sbom.json"))
    prev = ROOT / str(policy.get("sbom_previous_path", "evidence/security/sbom.previous.json"))
    approval = ROOT / str(policy.get("sbom_diff_approval_path", "governance/security/sbom_diff_approval.json"))

    findings: list[str] = []
    if not cur.exists():
        findings.append("missing_current_sbom")
    if not approval.exists():
        findings.append("missing_sbom_diff_approval")

    added: list[str] = []
    removed: list[str] = []
    if cur.exists() and prev.exists():
        c = _packages(cur)
        p = _packages(prev)
        added = sorted(c - p)
        removed = sorted(p - c)
        if added or removed:
            sig = approval.with_suffix(approval.suffix + ".sig")
            sig_ok = sig.exists() and verify_file(
                approval,
                sig.read_text(encoding="utf-8").strip(),
                key=current_key(strict=False),
            )
            if not sig_ok:
                findings.append("missing_or_invalid_approval_signature")
            ap = json.loads(approval.read_text(encoding="utf-8"))
            approved = set(ap.get("allowed_changes", [])) if isinstance(ap, dict) else set()
            for item in added:
                if f"+{item}" not in approved:
                    findings.append(f"unapproved_sbom_addition:{item}")
            for item in removed:
                if f"-{item}" not in approved:
                    findings.append(f"unapproved_sbom_removal:{item}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"added": added, "removed": removed, "previous_exists": prev.exists()},
        "metadata": {"gate": "sbom_diff_review_gate"},
    }
    out = evidence_root() / "security" / "sbom_diff_review_gate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"SBOM_DIFF_REVIEW_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
