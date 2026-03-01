#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

WAIVER_ADRS = [
    "evidence/repro/decisions/ADR-2026-03-01-m12-resource-gap-temporary-waiver.md",
    "evidence/repro/decisions/ADR-2026-03-01-m18-device-resource-gap-temporary-waiver.md",
    "evidence/repro/decisions/ADR-2026-03-01-m19-proceed-under-m18-waiver.md",
    "evidence/repro/decisions/ADR-2026-03-01-m23-progress-with-limited-cluster.md",
    "evidence/repro/decisions/ADR-2026-03-01-m24-progress-with-limited-targets.md",
]


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run(cmd: list[str]) -> tuple[int, str, str]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except FileNotFoundError as exc:
        return 127, "", str(exc)


def _android_status() -> dict[str, Any]:
    code, out, err = _run(["adb", "devices"])
    if code != 0:
        return {"target": "android", "status": "BLOCKED", "classification": "E2", "reason": err or out or "adb not available"}
    lines = [ln for ln in out.splitlines() if ln.strip() and not ln.startswith("List of devices")]
    online = [ln for ln in lines if "\tdevice" in ln]
    if not online:
        return {"target": "android", "status": "BLOCKED", "classification": "E2", "reason": "adb present but no device connected"}
    return {"target": "android", "status": "PASS", "classification": "E1", "reason": "Android target detected.", "devices": online}


def _ios_status() -> dict[str, Any]:
    code, out, err = _run(["xcrun", "simctl", "list", "devices"])
    if code != 0:
        return {"target": "ios", "status": "BLOCKED", "classification": "E2", "reason": err or out or "xcrun/simctl not available"}
    # Any Booted or Shutdown simulator entry indicates iOS runtime availability on host.
    lines = [ln.strip() for ln in out.splitlines() if "(" in ln and ")" in ln]
    if not lines:
        return {"target": "ios", "status": "BLOCKED", "classification": "E2", "reason": "xcrun present but no simulators listed"}
    return {"target": "ios", "status": "PASS", "classification": "E1", "reason": "iOS simulator/runtime detected.", "simulators_count": len(lines)}


def _web_status() -> dict[str, Any]:
    for cmd in (["node", "--version"], ["wasmtime", "--version"], ["wasmer", "--version"]):
        code, out, err = _run(cmd)
        if code == 0:
            return {
                "target": "web",
                "status": "PASS",
                "classification": "E1",
                "reason": "Web runtime toolchain detected.",
                "runtime_cmd": " ".join(cmd),
                "runtime_version": out or err,
            }
    return {"target": "web", "status": "BLOCKED", "classification": "E2", "reason": "No Node.js/Wasm runtime detected"}


def _runtime_meta() -> dict[str, Any]:
    return {
        "platform": platform.platform(),
        "kernel": platform.release(),
        "python": platform.python_version(),
        "timestamp_utc": datetime.now(UTC).isoformat(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Milestone 24 edge/mobile/web runtime coverage.")
    parser.add_argument(
        "--output-dir",
        default=str(ROOT / "evidence" / "repro" / "milestone-24-edge-mobile-web"),
    )
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    checks = [_android_status(), _ios_status(), _web_status()]
    statuses = [c["status"] for c in checks]
    if any(s == "FAIL" for s in statuses):
        overall_status, overall_class, overall_reason = "FAIL", "E2", "At least one edge/mobile/web target failed."
    elif any(s == "BLOCKED" for s in statuses):
        overall_status, overall_class, overall_reason = "BLOCKED", "E2", "At least one edge/mobile/web target is blocked."
    else:
        overall_status, overall_class, overall_reason = "PASS", "E1", "All edge/mobile/web targets are available."

    report = {
        "milestone": 24,
        "profile": "edge_mobile_web",
        "status": overall_status,
        "classification": overall_class,
        "reason": overall_reason,
        "checks": checks,
        "meta": _runtime_meta(),
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "repro-classification.json").write_text(
        json.dumps(
            {
                "milestone": 24,
                "profile": "edge_mobile_web",
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
            {"pairs": [{"pair": "edge_mobile_web_targets", "status": overall_status, "classification": overall_class, "reason": overall_reason}]},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (out_dir / "env-matrix.json").write_text(json.dumps(report["meta"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "coverage-summary.json").write_text(json.dumps({"milestone": 24, "target_count": len(checks), "status": overall_status}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "device-matrix.json").write_text(json.dumps({"targets": [c["target"] for c in checks]}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "os-matrix.json").write_text(json.dumps({"note": "Target runtime detection is host-specific for mobile/web tooling."}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "language-matrix.json").write_text(json.dumps({"note": "Milestone 24 focuses on runtime targets, not language lanes."}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "library-matrix.json").write_text(json.dumps({"note": "Milestone 24 validates runtime target availability and reproducibility readiness."}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    gaps = ["# Portability Gaps (Milestone 24)", ""]
    for c in checks:
        if c["status"] != "PASS":
            gaps.append(f"- `{c['target']}`: {c['reason']}")
    if len(gaps) == 2:
        gaps.append("- No portability gaps detected.")
    (out_dir / "portability-gaps.md").write_text("\n".join(gaps) + "\n", encoding="utf-8")
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
                "# Milestone 24: Edge, Mobile, and Web Runtime Coverage",
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
        "# Known Limitations (Milestone 24)\n\n"
        "- Full PASS requires real Android/iOS/Web runtime targets connected or available.\n"
        "- iOS checks require macOS host tooling (`xcrun simctl`).\n",
        encoding="utf-8",
    )
    (out_dir / "milestone.json").write_text(
        json.dumps(
            {
                "milestone": 24,
                "slug": "edge-mobile-web",
                "owner": "Astrocytech/Glyphser",
                "target_date": "2027-02-18",
                "dependencies": [23],
                "profiles": ["edge_mobile_web"],
                "result": overall_status,
                "classification": overall_class,
                "evidence_dir": "evidence/repro/milestone-24-edge-mobile-web/",
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
