#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import socket
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

WAIVER_ADR_M18 = "evidence/repro/decisions/ADR-2026-03-01-m18-device-resource-gap-temporary-waiver.md"
WAIVER_ADR_M19 = "evidence/repro/decisions/ADR-2026-03-01-m19-proceed-under-m18-waiver.md"


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run(cmd: list[str]) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except FileNotFoundError as exc:
        return 127, "", str(exc)


def _linux_distro() -> str:
    os_release = Path("/etc/os-release")
    if not os_release.exists():
        return ""
    text = os_release.read_text(encoding="utf-8", errors="ignore")
    pretty = ""
    for line in text.splitlines():
        if line.startswith("PRETTY_NAME="):
            pretty = line.split("=", 1)[1].strip().strip('"')
            break
    return pretty


def _is_wsl() -> bool:
    if platform.system().lower() != "linux":
        return False
    env_hit = any(k in ("WSL_INTEROP", "WSL_DISTRO_NAME") for k in dict(**{}).keys())
    # direct env check
    if "WSL_INTEROP" in __import__("os").environ or "WSL_DISTRO_NAME" in __import__("os").environ:
        return True
    rel = platform.release().lower()
    plat = platform.platform().lower()
    return "microsoft" in rel or "wsl" in plat or env_hit


def _collect_local_manifest() -> dict[str, Any]:
    os_family = platform.system()
    arch = platform.machine().lower()
    distro = _linux_distro() if os_family.lower() == "linux" else ""
    return {
        "host_id": socket.gethostname(),
        "source": "local",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "os_family": os_family,
        "platform": platform.platform(),
        "kernel": platform.release(),
        "python": platform.python_version(),
        "arch": arch,
        "linux_distro": distro,
        "is_wsl": _is_wsl(),
    }


def _load_manifest(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _is_windows_native(host: dict[str, Any]) -> bool:
    os_family = str(host.get("os_family", "")).lower()
    return os_family.startswith("windows") and not bool(host.get("is_wsl", False))


def _is_macos_arm64(host: dict[str, Any]) -> bool:
    os_family = str(host.get("os_family", "")).lower()
    arch = str(host.get("arch", "")).lower()
    return os_family == "darwin" and arch in {"arm64", "aarch64"}


def _is_linux_host(host: dict[str, Any]) -> bool:
    return str(host.get("os_family", "")).lower().startswith("linux")


def _is_ubuntu_lts(host: dict[str, Any]) -> bool:
    distro = str(host.get("linux_distro", "")).lower()
    return "ubuntu" in distro and re.search(r"\b(20\.04|22\.04|24\.04|26\.04)\b", distro) is not None


def _is_non_ubuntu_linux(host: dict[str, Any]) -> bool:
    if not _is_linux_host(host):
        return False
    distro = str(host.get("linux_distro", "")).lower()
    if not distro:
        return False
    return "ubuntu" not in distro


def _runtime_meta() -> dict[str, Any]:
    return {
        "platform": platform.platform(),
        "kernel": platform.release(),
        "python": platform.python_version(),
        "timestamp_utc": datetime.now(UTC).isoformat(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Milestone 19 OS universality matrix.")
    parser.add_argument(
        "--host-manifest",
        action="append",
        default=[],
        help="Additional host manifest json files.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(ROOT / "evidence" / "repro" / "milestone-19-os-universality"),
    )
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    local = _collect_local_manifest()
    local_path = out_dir / f"host-{local['host_id']}.json"
    local_path.write_text(json.dumps(local, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    hosts = [local]
    for p in args.host_manifest:
        path = Path(p)
        if not path.is_absolute():
            path = ROOT / path
        hosts.append(_load_manifest(path))

    checks = [
        ("ubuntu_lts_linux", _is_ubuntu_lts),
        ("additional_non_ubuntu_linux", _is_non_ubuntu_linux),
        ("windows_11_native", _is_windows_native),
        ("macos_apple_silicon", _is_macos_arm64),
    ]

    matrix_rows: list[dict[str, Any]] = []
    missing: list[str] = []
    for name, predicate in checks:
        matches = [h.get("host_id", "unknown") for h in hosts if predicate(h)]
        present = bool(matches)
        if not present:
            missing.append(name)
        matrix_rows.append(
            {
                "os_target": name,
                "status": "PASS" if present else "BLOCKED",
                "present_hosts": matches,
            }
        )

    if missing:
        overall_status, overall_class = "BLOCKED", "E2"
        overall_reason = "Missing OS targets: " + ", ".join(missing)
    else:
        overall_status, overall_class = "PASS", "E0"
        overall_reason = "All required OS targets are covered."

    report = {
        "milestone": 19,
        "profile": "os_universality",
        "status": overall_status,
        "classification": overall_class,
        "reason": overall_reason,
        "os_matrix": matrix_rows,
        "hosts": hosts,
        "meta": _runtime_meta(),
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "repro-classification.json").write_text(
        json.dumps(
            {
                "milestone": 19,
                "profile": "os_universality",
                "classification": overall_class,
                "status": overall_status,
                "reason": overall_reason,
                "excluded_operators": [],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (out_dir / "os-matrix.json").write_text(
        json.dumps({"os_matrix": matrix_rows}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "pair-matrix.json").write_text(
        json.dumps(
            {
                "pairs": [
                    {
                        "pair": "os_target_coverage",
                        "status": overall_status,
                        "classification": overall_class,
                        "reason": overall_reason,
                    }
                ]
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (out_dir / "env-matrix.json").write_text(
        json.dumps(report["meta"], indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (out_dir / "coverage-summary.json").write_text(
        json.dumps(
            {
                "milestone": 19,
                "host_count": len(hosts),
                "os_families": sorted({str(h.get("os_family", "")) for h in hosts}),
                "status": overall_status,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (out_dir / "device-matrix.json").write_text(
        json.dumps(
            {"note": "Milestone 19 focuses on OS targets; device-class universality is milestone 18."},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (out_dir / "language-matrix.json").write_text(
        json.dumps(
            {"note": "Milestone 19 focuses on OS targets; language universality is milestone 20."},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (out_dir / "library-matrix.json").write_text(
        json.dumps(
            {"note": "Milestone 19 focuses on OS targets; library universality is milestone 21."},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    gaps = ["# Portability Gaps (Milestone 19)", ""]
    if missing:
        for m in missing:
            gaps.append(f"- Missing `{m}`: add host manifest and rerun matrix.")
    else:
        gaps.append("- No portability gaps in required OS targets.")
    (out_dir / "portability-gaps.md").write_text("\n".join(gaps) + "\n", encoding="utf-8")

    waivers: list[dict[str, Any]] = []
    for adr in (WAIVER_ADR_M18, WAIVER_ADR_M19):
        if (ROOT / adr).exists():
            waivers.append({"adr": adr, "status": "ACTIVE"})
    (out_dir / "waivers.json").write_text(
        json.dumps({"waivers": waivers}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    conformance_hashes: dict[str, Any] = {"status": overall_status}
    results_path = ROOT / "evidence" / "conformance" / "results" / "latest.json"
    report_path = ROOT / "evidence" / "conformance" / "reports" / "latest.json"
    if results_path.exists():
        conformance_hashes["conformance_results"] = {
            "path": "evidence/conformance/results/latest.json",
            "sha256": _sha256_file(results_path),
        }
    if report_path.exists():
        conformance_hashes["conformance_report"] = {
            "path": "evidence/conformance/reports/latest.json",
            "sha256": _sha256_file(report_path),
        }
    (out_dir / "conformance-hashes.json").write_text(
        json.dumps(conformance_hashes, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    (out_dir / "summary.md").write_text(
        "\n".join(
            [
                "# Milestone 19: Operating System Universality Matrix",
                "",
                f"Status: {overall_status}",
                f"Classification: {overall_class}",
                f"Reason: {overall_reason}",
                "",
                f"Hosts observed: {len(hosts)}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (out_dir / "known-limitations.md").write_text(
        "# Known Limitations (Milestone 19)\n\n"
        "- WSL hosts are reported as Linux and do not satisfy Windows-native requirement.\n"
        "- macOS requirement is explicitly Apple Silicon (`arm64`) for this milestone.\n",
        encoding="utf-8",
    )
    (out_dir / "milestone.json").write_text(
        json.dumps(
            {
                "milestone": 19,
                "slug": "os-universality",
                "owner": "Astrocytech/Glyphser",
                "target_date": "2026-10-01",
                "dependencies": [18],
                "waiver_dependencies": [18],
                "profiles": ["os_matrix"],
                "result": overall_status,
                "classification": overall_class,
                "evidence_dir": "evidence/repro/milestone-19-os-universality/",
                "host_manifests": [str(local_path.relative_to(ROOT))] + args.host_manifest,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "status": overall_status,
                "classification": overall_class,
                "reason": overall_reason,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if overall_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
