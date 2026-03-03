from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def _classify(findings: list[str]) -> str:
    if not findings:
        return "none"
    text = " ".join(findings)
    if "missing" in text:
        return "missing_artifact"
    if "mismatch" in text:
        return "contract_mismatch"
    if "coverage" in text:
        return "coverage_failure"
    if "invalid" in text:
        return "invalid_structure"
    return "unknown"


def _recommendations(category: str) -> list[str]:
    table = {
        "none": ["No action required."],
        "missing_artifact": [
            "Regenerate required artifacts using make release-check.",
            "Verify fixture/spec paths in gate configuration.",
        ],
        "contract_mismatch": [
            "Compare expected vs actual hashes and API contracts.",
            "Update spec or implementation and matching tests in one PR.",
        ],
        "coverage_failure": [
            "Add tests for uncovered critical-path modules.",
            "Re-run coverage and module coverage gate locally.",
        ],
        "invalid_structure": [
            "Validate JSON/schema shape before committing artifacts.",
            "Regenerate artifacts from canonical tooling scripts.",
        ],
        "unknown": [
            "Inspect gate findings and raw outputs.",
            "Create issue with gate trace payload and failing artifacts.",
        ],
    }
    return table.get(category, table["unknown"])


def emit_gate_trace(root: Path, gate_id: str, report: dict[str, Any]) -> Path:
    findings = [str(x) for x in report.get("findings", [])]
    category = _classify(findings)
    payload = {
        "schema_version": "glyphser-gate-telemetry.v1",
        "gate_id": gate_id,
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "status": report.get("status", "UNKNOWN"),
        "findings": findings,
        "failure_taxonomy": category,
        "recommended_next_steps": _recommendations(category),
        "raw_report": report,
    }
    out = root / "evidence" / "gates" / "telemetry" / f"{gate_id}.trace.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out
