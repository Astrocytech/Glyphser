#!/usr/bin/env python3
from __future__ import annotations

import argparse
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

POLICY = ROOT / "governance" / "security" / "attestation_index_signed_artifacts_policy.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _required_for_lane(policy: dict[str, Any], lane: str) -> list[str]:
    lane_map = policy.get("lane_required_signed_artifacts", {})
    if isinstance(lane_map, dict):
        lane_items = lane_map.get(lane, [])
        if isinstance(lane_items, list):
            normalized = [str(item).strip() for item in lane_items if str(item).strip()]
            if normalized:
                return normalized
    defaults = policy.get("default_required_signed_artifacts", [])
    if isinstance(defaults, list):
        return [str(item).strip() for item in defaults if str(item).strip()]
    return []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate required signed artifacts are present in attestation index.")
    parser.add_argument("--lane", default="default", help="Lane key used to resolve required signed artifacts policy.")
    args = parser.parse_args([] if argv is None else argv)

    sec = evidence_root() / "security"
    findings: list[str] = []

    if not POLICY.exists():
        findings.append("missing_attestation_index_signed_artifacts_policy")
        policy = {}
    else:
        try:
            policy = _load_json(POLICY)
        except Exception:
            policy = {}
            findings.append("invalid_attestation_index_signed_artifacts_policy")

    required = _required_for_lane(policy, args.lane)
    if not required:
        findings.append(f"missing_required_signed_artifacts_for_lane:{args.lane}")

    index_path = sec / "evidence_attestation_index.json"
    if not index_path.exists():
        findings.append("missing_evidence_attestation_index")
        indexed_paths: set[str] = set()
    else:
        try:
            payload = _load_json(index_path)
        except Exception:
            payload = {}
            findings.append("invalid_evidence_attestation_index")
        items = payload.get("items", []) if isinstance(payload, dict) else []
        indexed_paths = {
            str(item.get("path", "")).strip()
            for item in items
            if isinstance(item, dict) and str(item.get("path", "")).strip()
        }

    for artifact in required:
        if artifact not in indexed_paths:
            findings.append(f"missing_attestation_index_signed_artifact:{args.lane}:{artifact}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "lane": args.lane,
            "required_signed_artifacts": len(required),
            "indexed_artifacts": len(indexed_paths),
        },
        "metadata": {
            "gate": "attestation_index_signed_artifacts_gate",
            "policy_path": str(POLICY.relative_to(ROOT)),
        },
    }
    out = sec / "attestation_index_signed_artifacts_gate.json"
    write_json_report(out, report)
    print(f"ATTESTATION_INDEX_SIGNED_ARTIFACTS_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
