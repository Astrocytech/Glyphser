#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
current_key = artifact_signing.current_key
sign_file = artifact_signing.sign_file
verify_file = artifact_signing.verify_file
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report
compliance_delta = importlib.import_module("tooling.security.governance_compliance_delta_report")


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _quarter_label(ts: datetime) -> str:
    quarter = ((ts.month - 1) // 3) + 1
    return f"{ts.year}-Q{quarter}"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    findings: list[str] = []

    # Ensure the latest compliance delta is available for this quarter snapshot.
    rc = compliance_delta.main([])
    src = sec / "governance_compliance_delta_report.json"
    if rc != 0 or not src.exists():
        findings.append("missing_or_invalid_compliance_delta_source")
        source_payload: dict[str, Any] = {}
    else:
        try:
            source_payload = _load_json(src)
        except Exception:
            source_payload = {}
            findings.append("invalid_compliance_delta_source_json")

    now = datetime.now(UTC)
    quarter = _quarter_label(now)
    source_status = str(source_payload.get("status", "UNKNOWN")).upper() if source_payload else "UNKNOWN"
    if source_status in {"WARN", "FAIL", "UNKNOWN"}:
        findings.append(f"source_compliance_status:{source_status}")

    snapshot = {
        "status": "PASS" if not findings else ("WARN" if not any(x.startswith("missing_or_invalid") or x.startswith("invalid_") for x in findings) else "FAIL"),
        "findings": findings,
        "summary": {
            "quarter": quarter,
            "generated_at_utc": now.isoformat(),
            "source_report_path": str(src.relative_to(ROOT)).replace("\\", "/") if src.exists() else "",
            "source_report_sha256": f"sha256:{_sha256(src)}" if src.exists() else "",
            "source_compliance_status": source_status,
        },
        "metadata": {"gate": "governance_compliance_quarterly_snapshot"},
    }

    out = sec / "governance_compliance_quarterly_snapshot.json"
    write_json_report(out, snapshot)

    sig_path = out.with_suffix(".json.sig")
    signature = sign_file(out, key=current_key(strict=False))
    sig_path.write_text(signature + "\n", encoding="utf-8")
    if not verify_file(out, signature, key=current_key(strict=False)):
        snapshot["status"] = "FAIL"
        snapshot.setdefault("findings", []).append("quarterly_snapshot_signature_invalid")
        write_json_report(out, snapshot)

    print(f"GOVERNANCE_COMPLIANCE_QUARTERLY_SNAPSHOT: {snapshot['status']}")
    print(f"Snapshot: {out}")
    print(f"Signature: {sig_path}")
    return 1 if snapshot["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
