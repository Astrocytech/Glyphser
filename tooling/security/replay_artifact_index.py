#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

REQUIRED_SECURITY_REPORTS = (
    "security_super_gate.json",
    "ci_incident_replay_harness.json",
    "tabletop_replay.json",
    "deterministic_replay_harness.json",
    "replay_nondeterministic_field_drift_gate.json",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate replay artifact index for forensic reconstruction.")
    parser.add_argument("--run-dir", required=True, help="Saved run directory containing security and incident artifacts.")
    args = parser.parse_args([] if argv is None else argv)

    run_dir = Path(args.run_dir)
    if not run_dir.is_absolute():
        run_dir = (ROOT / run_dir).resolve()

    security_dir = run_dir / "security"
    incident_dir = run_dir / "incident"
    findings: list[str] = []
    entries: list[dict[str, Any]] = []

    for name in REQUIRED_SECURITY_REPORTS:
        path = security_dir / name
        if not path.exists():
            findings.append(f"missing_replay_artifact:{name}")
            continue
        entries.append(
            {
                "path": f"security/{name}",
                "size_bytes": path.stat().st_size,
                "sha256": _sha256(path),
                "kind": "security_report",
            }
        )

    incident_artifacts = sorted(incident_dir.glob("incident-bundle-*.tar.gz")) if incident_dir.exists() else []
    if not incident_artifacts:
        findings.append("missing_incident_bundle_tarball")
    for path in incident_artifacts:
        rel = path.relative_to(run_dir).as_posix()
        entries.append(
            {
                "path": rel,
                "size_bytes": path.stat().st_size,
                "sha256": _sha256(path),
                "kind": "incident_bundle",
            }
        )
        sha_path = path.with_suffix(path.suffix + ".sha256")
        manifest_path = path.with_suffix(path.suffix + ".manifest.json")
        for companion, kind in ((sha_path, "incident_bundle_digest"), (manifest_path, "incident_bundle_manifest")):
            if not companion.exists():
                findings.append(f"missing_incident_bundle_companion:{companion.name}")
                continue
            entries.append(
                {
                    "path": companion.relative_to(run_dir).as_posix(),
                    "size_bytes": companion.stat().st_size,
                    "sha256": _sha256(companion),
                    "kind": kind,
                }
            )

    entries = sorted(entries, key=lambda item: str(item.get("path", "")))
    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"run_dir": str(run_dir), "indexed_artifacts": len(entries)},
        "metadata": {"gate": "replay_artifact_index"},
        "artifacts": entries,
    }
    out = evidence_root() / "security" / "replay_artifact_index.json"
    write_json_report(out, report)
    print(f"REPLAY_ARTIFACT_INDEX: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
