#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
import importlib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tooling.lib.path_config import evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

_TARGET_TO_FILE = {
    "branch_protection": "branch_protection_live.json",
    "live_integrations": "live_integrations.json",
}


def _load_policy() -> dict[str, Any]:
    policy_path = ROOT / "governance" / "security" / "live_rollout_policy.json"
    data = json.loads(policy_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("invalid live rollout policy")
    return data


def _parse_checked_at(text: str) -> datetime:
    return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(UTC)


def _verify_target(
    target: str,
    *,
    max_age_hours: int,
    allow_dry_run: bool,
    allow_missing: bool,
) -> list[str]:
    findings: list[str] = []
    path = evidence_root() / "security" / _TARGET_TO_FILE[target]
    if not path.exists():
        if not allow_missing:
            findings.append(f"{target}: missing evidence file {path.relative_to(ROOT)}")
        return findings

    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        findings.append(f"{target}: evidence payload must be object")
        return findings

    if payload.get("status") != "PASS":
        findings.append(f"{target}: status is not PASS")
    mode = str(payload.get("mode", "")).strip()
    if not allow_dry_run and mode != "live":
        findings.append(f"{target}: mode must be live")
    checked_at = str(payload.get("checked_at_utc", "")).strip()
    if not checked_at:
        findings.append(f"{target}: missing checked_at_utc")
    else:
        age_hours = int((datetime.now(UTC) - _parse_checked_at(checked_at)).total_seconds() // 3600)
        if age_hours > max_age_hours:
            findings.append(f"{target}: evidence stale ({age_hours}h > {max_age_hours}h)")
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify live rollout evidence freshness/completeness.")
    parser.add_argument(
        "--target",
        action="append",
        choices=sorted(_TARGET_TO_FILE.keys()),
        help="Target evidence to verify (default: all).",
    )
    parser.add_argument("--allow-dry-run", action="store_true")
    parser.add_argument("--allow-missing", action="store_true")
    parser.add_argument("--max-age-hours", type=int, default=0, help="Override policy max age in hours.")
    parser.add_argument("--profile", choices=["default", "release"], default="default")
    args = parser.parse_args([] if argv is None else argv)

    policy = _load_policy()
    policy_age_key = "release_max_evidence_age_hours" if args.profile == "release" else "max_evidence_age_hours"
    max_age_hours = args.max_age_hours or int(policy.get(policy_age_key, policy.get("max_evidence_age_hours", 168)))
    targets = args.target or list(_TARGET_TO_FILE.keys())
    findings: list[str] = []
    for target in targets:
        findings.extend(
            _verify_target(
                target,
                max_age_hours=max_age_hours,
                allow_dry_run=args.allow_dry_run,
                allow_missing=args.allow_missing,
            )
        )

    payload = {
        "status": "PASS" if not findings else "FAIL",
        "targets": targets,
        "max_evidence_age_hours": max_age_hours,
        "allow_dry_run": args.allow_dry_run,
        "allow_missing": args.allow_missing,
        "profile": args.profile,
        "findings": findings,
        "summary": {
            "target_count": len(targets),
            "finding_count": len(findings),
            "max_evidence_age_hours": max_age_hours,
        },
        "metadata": {"gate": "live_rollout_gate"},
    }
    out = evidence_root() / "security" / "live_rollout_gate.json"
    write_json_report(out, payload)
    print(f"LIVE_ROLLOUT_GATE: {payload['status']}")
    print(f"Report: {out}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
