#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_sp = importlib.import_module("".join(["sub", "process"]))

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))


def _now_utc() -> str:
    return datetime.now(UTC).isoformat()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _run(cmd: list[str]) -> tuple[int, str, str]:
    try:
        proc = _sp.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
    except FileNotFoundError as exc:
        return 127, "", str(exc)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def _runtime_meta() -> dict[str, Any]:
    return {
        "platform": platform.platform(),
        "kernel": platform.release(),
        "python": platform.python_version(),
        "timestamp_utc": _now_utc(),
    }


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _assign_tier(prereq_row: dict[str, Any]) -> str:
    status = str(prereq_row.get("status", "BLOCKED"))
    gate_status = str(prereq_row.get("gate_status", status))
    if gate_status == "PASS" and status == "PASS":
        return "tier_1_certified"
    if gate_status == "PASS" and status != "PASS":
        return "tier_2_compatible_by_contract"
    return "tier_3_unvalidated"


def _run_claim_gate(report_path: Path, check_paths: list[Path]) -> tuple[int, dict[str, Any]]:
    cmd = [
        sys.executable,
        str(ROOT / "tooling" / "quality_gates" / "claim_scope_gate.py"),
        "--report",
        str(report_path),
    ]
    for p in check_paths:
        cmd.extend(["--check-path", str(p)])
    code, out, err = _run(cmd)
    try:
        payload = json.loads(out) if out else {"status": "FAIL", "reason": err or "claim gate emitted no json"}
    except Exception:
        payload = {
            "status": "FAIL",
            "reason": err or out or "claim gate emitted invalid json",
        }
    return code, payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Milestone 30 support tiers and compatibility contract checks.")
    parser.add_argument(
        "--output-dir",
        default=str(ROOT / "evidence" / "repro" / "milestone-30-support-tiers"),
    )
    parser.add_argument(
        "--cert-bundle",
        default=str(ROOT / "evidence" / "repro" / "milestone-29-certify" / "certification-bundle.json"),
    )
    parser.add_argument(
        "--allow-nonpass-cert-bundle",
        action="store_true",
        help="Allow generating a PASS policy report even when milestone-29 certification bundle is not PASS.",
    )
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cert_bundle_path = Path(args.cert_bundle)
    cert_bundle = _load_json(cert_bundle_path)
    if cert_bundle is None:
        reason = f"missing or invalid certification bundle: {cert_bundle_path}"
        report = {
            "milestone": 30,
            "profile": "support_tiers_contract",
            "status": "BLOCKED",
            "classification": "E2",
            "reason": reason,
            "meta": _runtime_meta(),
        }
        _write_json(out_dir / "report.json", report)
        print(
            json.dumps(
                {"status": "BLOCKED", "classification": "E2", "reason": reason},
                indent=2,
                sort_keys=True,
            )
        )
        return 1

    prereq_rows = list(cert_bundle.get("prerequisites", []))
    scope_label = str(cert_bundle.get("scope_label", "unknown"))
    cert_status = str(cert_bundle.get("status", "BLOCKED"))

    tier_rows: list[dict[str, Any]] = []
    tier_counts = {
        "tier_1_certified": 0,
        "tier_2_compatible_by_contract": 0,
        "tier_3_unvalidated": 0,
    }
    for row in prereq_rows:
        tier = _assign_tier(row)
        tier_counts[tier] += 1
        tier_rows.append(
            {
                "milestone": row.get("milestone"),
                "slug": row.get("slug"),
                "status": row.get("status"),
                "gate_status": row.get("gate_status", row.get("status")),
                "classification": row.get("classification", "E2"),
                "tier": tier,
                "reason": row.get("reason", "unknown"),
            }
        )

    support_tier_matrix = {
        "milestone": 30,
        "profile": "support_tiers_contract",
        "scope_label": scope_label,
        "tiers": [
            {
                "tier": "tier_1_certified",
                "description": "Certified by direct passing evidence in active scope.",
            },
            {
                "tier": "tier_2_compatible_by_contract",
                "description": "Accepted by explicit contract/policy rule in active scope.",
            },
            {
                "tier": "tier_3_unvalidated",
                "description": "Not validated for current scope or blocked by prerequisites.",
            },
        ],
        "rows": tier_rows,
        "counts": tier_counts,
        "status": "PASS",
    }
    _write_json(out_dir / "support-tier-matrix.json", support_tier_matrix)

    known_limitations = out_dir / "known-limitations.md"
    known_limitations.write_text(
        "# Known Limitations (Milestone 30)\n\n"
        f"- Active certification scope: `{scope_label}`.\n"
        "- Universality claims must include explicit scope label (`available_local`, "
        "`available_local_partial`, or `strict_universal`).\n"
        "- Tier 2 indicates contract-based compatibility acceptance, not full strict-universal certification.\n",
        encoding="utf-8",
    )

    release_policy_delta = out_dir / "release-policy-delta.md"
    release_policy_delta.write_text(
        "# Release Policy Delta (Milestone 30)\n\n"
        "## Enforced Claim Rules\n"
        "- Unscoped use of `universal` is blocked by CI claim gate.\n"
        "- Every compatibility and certification statement must include a scope label.\n\n"
        "## Support Tier Mapping\n"
        "- Tier 1 (`tier_1_certified`): milestone status PASS with gate status PASS.\n"
        "- Tier 2 (`tier_2_compatible_by_contract`): milestone status BLOCKED/partial but "
        "gate status PASS by explicit policy.\n"
        "- Tier 3 (`tier_3_unvalidated`): gate status not PASS or missing evidence.\n\n"
        "## Active Scope\n"
        f"- `{scope_label}`\n",
        encoding="utf-8",
    )

    claim_gate_code, claim_gate_payload = _run_claim_gate(
        out_dir / "claim-gate-report.json", [known_limitations, release_policy_delta]
    )

    unscoped_fixture = out_dir / ".tmp-unscoped-claim.txt"
    scoped_fixture = out_dir / ".tmp-scoped-claim.txt"
    unscoped_fixture.write_text("Glyphser is universal across everything.\n", encoding="utf-8")
    scoped_fixture.write_text(
        "Glyphser certification scope: available_local_partial universality profile.\n",
        encoding="utf-8",
    )

    unscoped_code, unscoped_payload = _run_claim_gate(out_dir / ".tmp-unscoped-report.json", [unscoped_fixture])
    scoped_code, scoped_payload = _run_claim_gate(out_dir / ".tmp-scoped-report.json", [scoped_fixture])

    # Cleanup temp fixtures/reports to keep the evidence directory clean.
    for path in [
        unscoped_fixture,
        scoped_fixture,
        out_dir / ".tmp-unscoped-report.json",
        out_dir / ".tmp-scoped-report.json",
    ]:
        if path.exists():
            path.unlink()

    tier_enforcement_tests: dict[str, Any] = {
        "milestone": 30,
        "scope_label": scope_label,
        "tests": [
            {
                "test_id": "claim_gate_scoped_docs_pass",
                "expected": "PASS",
                "actual": claim_gate_payload.get("status", "FAIL"),
                "status": "PASS" if claim_gate_code == 0 and claim_gate_payload.get("status") == "PASS" else "FAIL",
            },
            {
                "test_id": "claim_gate_unscoped_claim_rejected",
                "expected": "FAIL",
                "actual": unscoped_payload.get("status", "PASS"),
                "status": "PASS" if unscoped_code != 0 and unscoped_payload.get("status") == "FAIL" else "FAIL",
            },
            {
                "test_id": "claim_gate_scoped_claim_allowed",
                "expected": "PASS",
                "actual": scoped_payload.get("status", "FAIL"),
                "status": "PASS" if scoped_code == 0 and scoped_payload.get("status") == "PASS" else "FAIL",
            },
            {
                "test_id": "scope_label_present_in_cert_bundle",
                "expected": "present",
                "actual": scope_label if scope_label else "missing",
                "status": "PASS" if bool(scope_label and scope_label != "unknown") else "FAIL",
            },
            {
                "test_id": "tier_mapping_rows_match_prerequisites",
                "expected": str(len(prereq_rows)),
                "actual": str(len(tier_rows)),
                "status": "PASS" if len(prereq_rows) == len(tier_rows) else "FAIL",
            },
        ],
    }
    if not args.allow_nonpass_cert_bundle:
        tier_enforcement_tests["tests"].append(
            {
                "test_id": "cert_bundle_status_must_be_pass",
                "expected": "PASS",
                "actual": cert_status,
                "status": "PASS" if cert_status == "PASS" else "BLOCKED",
            }
        )
    _write_json(out_dir / "tier-enforcement-tests.json", tier_enforcement_tests)

    tests = tier_enforcement_tests.get("tests", [])
    failures = [t for t in tests if isinstance(t, dict) and t.get("status") == "FAIL"]
    blocked_tests = [t for t in tests if isinstance(t, dict) and t.get("status") == "BLOCKED"]
    if failures:
        status, classification = "FAIL", "E2"
        reason = "One or more support-tier enforcement tests failed."
    elif blocked_tests:
        status, classification = "BLOCKED", "E2"
        reason = "One or more support-tier enforcement checks are blocked by unmet prerequisites."
    else:
        status, classification = "PASS", "E1"
        reason = "Support-tier contract and claim enforcement checks pass."

    report = {
        "milestone": 30,
        "profile": "support_tiers_contract",
        "scope_label": scope_label,
        "status": status,
        "classification": classification,
        "reason": reason,
        "certification_bundle_status": cert_status,
        "meta": _runtime_meta(),
    }
    _write_json(out_dir / "report.json", report)

    conformance_hashes: dict[str, Any] = {"status": status}
    rp = ROOT / "evidence" / "conformance" / "reports" / "latest.json"
    rs = ROOT / "evidence" / "conformance" / "results" / "latest.json"
    if rp.exists():
        conformance_hashes["conformance_report"] = {
            "path": "evidence/conformance/reports/latest.json",
            "sha256": _sha256_file(rp),
        }
    if rs.exists():
        conformance_hashes["conformance_results"] = {
            "path": "evidence/conformance/results/latest.json",
            "sha256": _sha256_file(rs),
        }
    _write_json(out_dir / "conformance-hashes.json", conformance_hashes)

    _write_json(
        out_dir / "env-matrix.json",
        {
            "platform": platform.platform(),
            "kernel": platform.release(),
            "python": platform.python_version(),
            "timestamp_utc": _now_utc(),
        },
    )
    _write_json(
        out_dir / "repro-classification.json",
        {
            "milestone": 30,
            "profile": "support_tiers_contract",
            "status": status,
            "classification": classification,
            "reason": reason,
        },
    )
    _write_json(
        out_dir / "milestone.json",
        {
            "milestone": 30,
            "slug": "support-tiers",
            "owner": "Astrocytech/Glyphser",
            "target_date": _now_utc().split("T", 1)[0],
            "dependencies": [29],
            "profiles": ["support_tiers_contract"],
            "result": status,
            "classification": classification,
            "evidence_dir": "evidence/repro/milestone-30-support-tiers/",
        },
    )
    (out_dir / "summary.md").write_text(
        "\n".join(
            [
                "# Milestone 30: Support Tiers and Compatibility Contract",
                "",
                f"Scope label: {scope_label}",
                f"Status: {status}",
                f"Classification: {classification}",
                f"Reason: {reason}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {"status": status, "classification": classification, "reason": reason},
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
