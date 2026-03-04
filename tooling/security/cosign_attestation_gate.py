#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def main(argv: list[str] | None = None) -> int:
    _ = argv
    policy = json.loads((ROOT / "governance" / "security" / "container_provenance_policy.json").read_text(encoding="utf-8"))
    if not isinstance(policy, dict):
        raise ValueError("invalid container provenance policy")
    lane = os.environ.get("GLYPHSER_SECURITY_LANE", "").strip().lower() or "ci"
    required_lanes = {str(x).strip().lower() for x in policy.get("cosign_required_lanes", []) if isinstance(x, str)}
    skippable_lanes = {str(x).strip().lower() for x in policy.get("cosign_skippable_lanes", []) if isinstance(x, str)}
    required = [ROOT / "distribution" / "container" / "image-digests.txt"]
    for rel in [x for x in policy.get("required_signature_files", []) if isinstance(x, str)]:
        required.append(ROOT / rel)

    env_enabled = os.environ.get("GLYPHSER_CONTAINER_PUBLISHING_ENABLED", "").strip().lower()
    publishing_enabled = env_enabled in {"1", "true", "yes"}
    policy_publishing_enabled = bool(policy.get("container_publishing_enabled", False))
    has_any_attestation = any(p.exists() for p in required)
    strict_mode = (
        lane in required_lanes
        or publishing_enabled
        or policy_publishing_enabled
        or (bool(policy.get("required_when_container_artifacts_present", True)) and has_any_attestation)
    )
    if lane in skippable_lanes and not publishing_enabled and not policy_publishing_enabled:
        strict_mode = False

    missing = [str(p.relative_to(ROOT)).replace("\\", "/") for p in required if strict_mode and not p.exists()]
    report = {
        "status": "PASS" if not missing else "FAIL",
        "skipped": not strict_mode,
        "strict_mode": strict_mode,
        "findings": [f"missing_external_attestation:{m}" for m in missing],
        "summary": {
            "required_files": [str(p.relative_to(ROOT)).replace("\\", "/") for p in required],
            "lane": lane,
            "required_lanes": sorted(required_lanes),
            "skippable_lanes": sorted(skippable_lanes),
        },
        "metadata": {"gate": "cosign_attestation_gate"},
    }
    out = evidence_root() / "security" / "cosign_attestation_gate.json"
    write_json_report(out, report)
    print(f"COSIGN_ATTESTATION_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
