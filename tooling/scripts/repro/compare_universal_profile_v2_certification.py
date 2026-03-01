#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import platform
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]

REQUIRED_MILESTONES = {
    12: "milestone-12-multi-host-multi-os",
    16: "milestone-16-universal-profile-v1",
    18: "milestone-18-device-class-expansion",
    19: "milestone-19-os-universality",
    20: "milestone-20-language-ecosystem-v2",
    21: "milestone-21-library-ecosystem",
    22: "milestone-22-artifact-portability",
    23: "milestone-23-distributed-heterogeneous",
    24: "milestone-24-edge-mobile-web",
}

WAIVER_ADRS = [
    "evidence/repro/decisions/ADR-2026-03-01-m12-resource-gap-temporary-waiver.md",
    "evidence/repro/decisions/ADR-2026-03-01-m18-device-resource-gap-temporary-waiver.md",
    "evidence/repro/decisions/ADR-2026-03-01-m19-proceed-under-m18-waiver.md",
    "evidence/repro/decisions/ADR-2026-03-01-m23-progress-with-limited-cluster.md",
    "evidence/repro/decisions/ADR-2026-03-01-m24-progress-with-limited-targets.md",
    "evidence/repro/decisions/ADR-2026-03-01-m25-progress-with-blocked-prereqs.md",
]


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _runtime_meta() -> dict[str, Any]:
    return {
        "platform": platform.platform(),
        "kernel": platform.release(),
        "python": platform.python_version(),
        "timestamp_utc": datetime.now(UTC).isoformat(),
    }


def _load_report(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Milestone 25 universal profile v2 certification aggregator.")
    parser.add_argument(
        "--output-dir",
        default=str(ROOT / "evidence" / "repro" / "milestone-25-universal-profile-v2"),
    )
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    prereq_rows: list[dict[str, Any]] = []
    blocked: list[int] = []
    failed: list[int] = []
    missing: list[int] = []

    for mid, slug in REQUIRED_MILESTONES.items():
        report_path = ROOT / "evidence" / "repro" / slug / "report.json"
        report = _load_report(report_path)
        if report is None:
            prereq_rows.append(
                {
                    "milestone": mid,
                    "slug": slug,
                    "status": "BLOCKED",
                    "classification": "E2",
                    "reason": "missing report.json",
                    "report_path": str(report_path.relative_to(ROOT)),
                }
            )
            missing.append(mid)
            continue
        status = str(report.get("status", "BLOCKED"))
        classification = str(report.get("classification", "E2"))
        reason = str(report.get("reason", "unknown"))
        prereq_rows.append(
            {
                "milestone": mid,
                "slug": slug,
                "status": status,
                "classification": classification,
                "reason": reason,
                "report_path": str(report_path.relative_to(ROOT)),
            }
        )
        if status == "FAIL":
            failed.append(mid)
        elif status != "PASS":
            blocked.append(mid)

    if failed:
        overall_status, overall_class = "FAIL", "E2"
        overall_reason = "Failed prerequisite milestones: " + ", ".join(str(m) for m in failed)
    elif blocked or missing:
        overall_status, overall_class = "BLOCKED", "E2"
        all_blocked = sorted(set(blocked + missing))
        overall_reason = "Blocked prerequisite milestones: " + ", ".join(str(m) for m in all_blocked)
    else:
        overall_status, overall_class = "PASS", "E0"
        overall_reason = "All prerequisite milestones satisfied for Universal Profile v2 certification."

    compatibility_matrix = {
        "milestone": 25,
        "required_prerequisites": sorted(REQUIRED_MILESTONES.keys()),
        "rows": prereq_rows,
        "status": overall_status,
    }
    certification_bundle = {
        "milestone": 25,
        "profile": "universal_profile_v2",
        "status": overall_status,
        "classification": overall_class,
        "reason": overall_reason,
        "generated_at": datetime.now(UTC).isoformat(),
    }
    report = {
        "milestone": 25,
        "profile": "universal_profile_v2",
        "status": overall_status,
        "classification": overall_class,
        "reason": overall_reason,
        "prerequisites": prereq_rows,
        "meta": _runtime_meta(),
    }

    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "repro-classification.json").write_text(
        json.dumps(
            {
                "milestone": 25,
                "profile": "universal_profile_v2",
                "classification": overall_class,
                "status": overall_status,
                "reason": overall_reason,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (out_dir / "pair-matrix.json").write_text(
        json.dumps(
            {"pairs": [{"pair": "global_certification_gate", "status": overall_status, "classification": overall_class, "reason": overall_reason}]},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (out_dir / "coverage-summary.json").write_text(json.dumps({"milestone": 25, "prerequisite_count": len(prereq_rows), "status": overall_status}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "env-matrix.json").write_text(json.dumps(report["meta"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "device-matrix.json").write_text(json.dumps({"note": "Derived from prerequisite milestone reports."}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "os-matrix.json").write_text(json.dumps({"note": "Derived from prerequisite milestone reports."}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "language-matrix.json").write_text(json.dumps({"note": "Derived from prerequisite milestone reports."}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "library-matrix.json").write_text(json.dumps({"note": "Derived from prerequisite milestone reports."}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    gaps = ["# Portability Gaps (Milestone 25)", ""]
    for row in prereq_rows:
        if row["status"] != "PASS":
            gaps.append(f"- Milestone {row['milestone']} (`{row['slug']}`): {row['status']} - {row['reason']}")
    if len(gaps) == 2:
        gaps.append("- No portability gaps detected.")
    (out_dir / "portability-gaps.md").write_text("\n".join(gaps) + "\n", encoding="utf-8")
    (out_dir / "compatibility-matrix.json").write_text(json.dumps(compatibility_matrix, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "certification-bundle.json").write_text(json.dumps(certification_bundle, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    waivers = []
    for adr in WAIVER_ADRS:
        if (ROOT / adr).exists():
            waivers.append({"adr": adr, "status": "ACTIVE"})
    (out_dir / "waivers.json").write_text(json.dumps({"waivers": waivers}, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    conformance_hashes = {"status": overall_status}
    rp = ROOT / "evidence" / "conformance" / "reports" / "latest.json"
    rs = ROOT / "evidence" / "conformance" / "results" / "latest.json"
    if rp.exists():
        conformance_hashes["conformance_report"] = {"path": "evidence/conformance/reports/latest.json", "sha256": _sha256_file(rp)}
    if rs.exists():
        conformance_hashes["conformance_results"] = {"path": "evidence/conformance/results/latest.json", "sha256": _sha256_file(rs)}
    (out_dir / "conformance-hashes.json").write_text(json.dumps(conformance_hashes, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "summary.md").write_text(
        "\n".join(
            [
                "# Milestone 25: Universal Profile v2 Certification (Global)",
                "",
                f"Status: {overall_status}",
                f"Classification: {overall_class}",
                f"Reason: {overall_reason}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (out_dir / "known-limitations.md").write_text(
        "# Known Limitations (Milestone 25)\n\n"
        "- Certification status is computed from prerequisite milestone reports and remains blocked until all prerequisites PASS.\n",
        encoding="utf-8",
    )
    (out_dir / "milestone.json").write_text(
        json.dumps(
            {
                "milestone": 25,
                "slug": "universal-profile-v2",
                "owner": "Astrocytech/Glyphser",
                "target_date": "2027-03-20",
                "dependencies": sorted(REQUIRED_MILESTONES.keys()),
                "result": overall_status,
                "classification": overall_class,
                "evidence_dir": "evidence/repro/milestone-25-universal-profile-v2/",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print(json.dumps({"status": overall_status, "classification": overall_class, "reason": overall_reason}, indent=2, sort_keys=True))
    return 0 if overall_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
