#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "evidence" / "metadata" / "catalog.json"

TARGETS = [
    (
        "evidence/benchmarks/latest.json",
        "benchmark",
        "hello-core",
        "tooling/benchmarks/run_benchmarks.py",
        "glyphser-benchmark.v1",
    ),
    (
        "evidence/benchmarks/variance_impact.json",
        "benchmark",
        "hello-core",
        "tooling/benchmarks/variance_impact.py",
        "glyphser-variance-impact.v1",
    ),
    (
        "evidence/gates/structure/spec_impl_congruence.json",
        "gate",
        "contracts",
        "tooling/quality_gates/spec_impl_congruence_gate.py",
        "glyphser-gate-report.v1",
    ),
    (
        "evidence/traceability/index.json",
        "traceability",
        "all",
        "tooling/release/generate_traceability_index.py",
        "glyphser-traceability-index.v1",
    ),
    (
        "evidence/security/sbom.json",
        "security",
        "release",
        "tooling/security/security_artifacts.py",
        "glyphser-sbom-v1",
    ),
    (
        "evidence/security/build_provenance.json",
        "security",
        "release",
        "tooling/security/security_artifacts.py",
        "glyphser-provenance-v1",
    ),
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def generate() -> dict:
    entries = []
    for rel, evidence_type, source_fixture, generated_by, schema_version in TARGETS:
        p = ROOT / rel
        if not p.exists():
            continue
        entries.append(
            {
                "artifact_id": rel.replace("/", ".").replace(".json", ""),
                "path": rel,
                "sha256": _sha256(p),
                "evidence_type": evidence_type,
                "source_fixture": source_fixture,
                "generated_by": generated_by,
                "schema_version": schema_version,
            }
        )

    payload = {
        "schema_version": "glyphser-evidence-catalog.v1",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "generator": "tooling/release/generate_evidence_metadata.py",
        "entries": entries,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    _ = generate()
    print(str(OUT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
