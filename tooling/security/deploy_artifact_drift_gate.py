#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

POLICY = ROOT / "governance" / "security" / "deploy_artifact_drift_policy.json"


def _artifact_digests(path: Path) -> list[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return []
    raw = payload.get("artifact_digests", [])
    if not isinstance(raw, list):
        return []
    return sorted({str(x).strip() for x in raw if isinstance(x, str) and str(x).strip()})


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    if not POLICY.exists():
        raise ValueError("missing deploy_artifact_drift_policy.json")
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    if not isinstance(policy, dict):
        raise ValueError("invalid deploy artifact drift policy")

    deploy_manifest = ROOT / str(policy.get("deploy_manifest_path", "evidence/deploy/latest.json"))
    build_provenance = ROOT / str(policy.get("build_provenance_path", "evidence/security/build_provenance.json"))
    max_allowed_drift = int(policy.get("max_allowed_drift", 0))
    if max_allowed_drift < 0:
        raise ValueError("max_allowed_drift must be >= 0")

    build_digests = _artifact_digests(build_provenance) if build_provenance.exists() else []
    deploy_digests = _artifact_digests(deploy_manifest) if deploy_manifest.exists() else []
    if not build_provenance.exists():
        findings.append("missing_build_provenance")
    if not deploy_manifest.exists():
        findings.append("missing_deploy_manifest")
    if build_provenance.exists() and not build_digests:
        findings.append("missing_build_artifact_digests")
    if deploy_manifest.exists() and not deploy_digests:
        findings.append("missing_deploy_artifact_digests")

    build_set = set(build_digests)
    deploy_set = set(deploy_digests)
    drift = sorted(build_set.symmetric_difference(deploy_set))
    if len(drift) > max_allowed_drift:
        findings.append(f"artifact_drift_exceeds_policy:{len(drift)}>{max_allowed_drift}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "build_digest_count": len(build_digests),
            "deploy_digest_count": len(deploy_digests),
            "drift_count": len(drift),
            "max_allowed_drift": max_allowed_drift,
        },
        "metadata": {"gate": "deploy_artifact_drift_gate"},
    }
    out = evidence_root() / "security" / "deploy_artifact_drift_gate.json"
    write_json_report(out, report)
    print(f"DEPLOY_ARTIFACT_DRIFT_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
