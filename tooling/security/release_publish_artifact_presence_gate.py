#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


REQUIRED_SECURITY_ARTIFACTS = (
    "policy_signature.json",
    "provenance_signature.json",
    "evidence_attestation_gate.json",
    "security_super_gate.json",
    "release_rollback_provenance_gate.json",
    "rollback_handshake_artifact_gate.json",
)


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fail release publish when required security artifacts are missing."
    )
    parser.add_argument("--artifact-root", default=".", help="Root path where build artifacts were downloaded.")
    parser.add_argument("--run-id", default="", help="Release workflow run id (defaults to GITHUB_RUN_ID env if set).")
    parser.add_argument(
        "--build-lane",
        default="release-build",
        help="Build lane name used under evidence/runs/<run-id>/<build-lane>/security.",
    )
    parser.add_argument(
        "--report-path",
        default="",
        help="Optional explicit report output path. Defaults under artifact root evidence tree.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    run_id = str(args.run_id or "").strip()
    if not run_id:
        run_id = str(os.environ.get("GITHUB_RUN_ID", "")).strip()

    artifact_root = Path(args.artifact_root).resolve()
    findings: list[str] = []

    if not run_id:
        findings.append("missing_run_id")
        security_dir = artifact_root / "evidence" / "runs" / "<missing-run-id>" / args.build_lane / "security"
    else:
        security_dir = artifact_root / "evidence" / "runs" / run_id / args.build_lane / "security"

    missing_artifacts: list[str] = []
    for name in REQUIRED_SECURITY_ARTIFACTS:
        candidate = security_dir / name
        if not candidate.exists():
            rel = str(candidate.relative_to(artifact_root)).replace("\\", "/")
            findings.append(f"missing_required_security_artifact:{rel}")
            missing_artifacts.append(rel)

    if args.report_path:
        report_path = Path(args.report_path).resolve()
    else:
        report_path = security_dir / "release_publish_artifact_presence_gate.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "artifact_root": str(artifact_root),
            "run_id": run_id,
            "build_lane": args.build_lane,
            "required_security_artifact_count": len(REQUIRED_SECURITY_ARTIFACTS),
            "missing_security_artifact_count": len(missing_artifacts),
            "missing_security_artifacts": missing_artifacts,
        },
        "metadata": {"gate": "release_publish_artifact_presence_gate"},
    }
    write_json_report(report_path, report)
    print(f"RELEASE_PUBLISH_ARTIFACT_PRESENCE_GATE: {report['status']}")
    print(f"Report: {report_path}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
