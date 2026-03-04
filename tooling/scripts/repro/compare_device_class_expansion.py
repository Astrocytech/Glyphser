#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
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

WAIVER_ADR = "evidence/repro/decisions/ADR-2026-03-01-m12-resource-gap-temporary-waiver.md"

REQUIRED_DEVICE_CLASSES = [
    "cpu_x86_64",
    "cpu_arm64",
    "gpu_nvidia_cuda",
    "gpu_amd_rocm",
    "gpu_intel",
    "gpu_apple_mps",
    "edge_target",
]


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run(cmd: list[str]) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except FileNotFoundError as exc:
        return 127, "", str(exc)


def _has_nvidia_gpu() -> bool:
    code, out, _ = _run(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"])
    return code == 0 and bool(out.strip())


def _has_amd_rocm() -> bool:
    code, out, _ = _run(["rocminfo"])
    if code == 0 and out:
        return True
    if os.environ.get("ROCM_PATH") or os.environ.get("HIP_VISIBLE_DEVICES"):
        return True
    try:
        import torch  # type: ignore

        return bool(getattr(getattr(torch, "version", None), "hip", None))
    except Exception:
        return False


def _has_intel_gpu() -> bool:
    for cmd in (["sycl-ls"], ["clinfo"], ["lspci"]):
        code, out, _ = _run(cmd)
        if code == 0 and re.search(r"intel", out, re.IGNORECASE):
            return True
    return False


def _has_apple_mps() -> bool:
    if platform.system().lower() != "darwin":
        return False
    if platform.machine().lower() not in {"arm64", "aarch64"}:
        return False
    try:
        import torch  # type: ignore

        return bool(torch.backends.mps.is_available())  # type: ignore[attr-defined]
    except Exception:
        return True


def _has_edge_target() -> bool:
    env = os.environ.get("GLYPHSER_EDGE_TARGET", "").strip().lower()
    if env in {"1", "true", "yes"}:
        return True
    host_blob = " ".join([socket.gethostname(), platform.platform(), platform.node()]).lower()
    return any(tok in host_blob for tok in ("jetson", "raspberry", "rk3588", "edge"))


def _frameworks_meta() -> dict[str, Any]:
    out: dict[str, Any] = {}
    try:
        import torch  # type: ignore

        out["torch"] = {
            "present": True,
            "version": torch.__version__,
            "cuda_available": bool(torch.cuda.is_available()),
            "cuda_version": getattr(torch.version, "cuda", None),
            "hip_version": getattr(torch.version, "hip", None),
        }
    except Exception as exc:
        out["torch"] = {"present": False, "error": str(exc)}
    try:
        import tensorflow as tf  # type: ignore

        gpus = tf.config.list_physical_devices("GPU")
        out["tensorflow"] = {
            "present": True,
            "version": tf.__version__,
            "gpu_visible": bool(gpus),
        }
    except Exception as exc:
        out["tensorflow"] = {"present": False, "error": str(exc)}
    return out


def _collect_local_manifest() -> dict[str, Any]:
    machine = platform.machine().lower()
    classes = {
        "cpu_x86_64": machine in {"x86_64", "amd64"},
        "cpu_arm64": machine in {"arm64", "aarch64"},
        "gpu_nvidia_cuda": _has_nvidia_gpu(),
        "gpu_amd_rocm": _has_amd_rocm(),
        "gpu_intel": _has_intel_gpu(),
        "gpu_apple_mps": _has_apple_mps(),
        "edge_target": _has_edge_target(),
    }
    return {
        "host_id": socket.gethostname(),
        "source": "local",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "os_family": platform.system(),
        "platform": platform.platform(),
        "kernel": platform.release(),
        "python": platform.python_version(),
        "arch": machine,
        "device_classes": classes,
        "frameworks": _frameworks_meta(),
    }


def _load_manifest(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _runtime_meta() -> dict[str, Any]:
    return {
        "platform": platform.platform(),
        "kernel": platform.release(),
        "python": platform.python_version(),
        "timestamp_utc": datetime.now(UTC).isoformat(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Milestone 18 device-class expansion matrix.")
    parser.add_argument(
        "--host-manifest",
        action="append",
        default=[],
        help="Additional host manifest json files.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(ROOT / "evidence" / "repro" / "milestone-18-device-class-expansion"),
    )
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    local_manifest = _collect_local_manifest()
    local_path = out_dir / f"host-{local_manifest['host_id']}.json"
    local_path.write_text(json.dumps(local_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    hosts = [local_manifest]
    for p in args.host_manifest:
        path = Path(p)
        if not path.is_absolute():
            path = ROOT / path
        hosts.append(_load_manifest(path))

    matrix_rows: list[dict[str, Any]] = []
    missing: list[str] = []
    for cls in REQUIRED_DEVICE_CLASSES:
        present_hosts = [
            h.get("host_id", "unknown") for h in hosts if bool(h.get("device_classes", {}).get(cls, False))
        ]
        present = bool(present_hosts)
        if not present:
            missing.append(cls)
        matrix_rows.append(
            {
                "device_class": cls,
                "status": "PASS" if present else "BLOCKED",
                "present_hosts": present_hosts,
            }
        )

    if missing:
        overall_status = "BLOCKED"
        overall_class = "E2"
        overall_reason = "Missing required device classes: " + ", ".join(missing)
    else:
        overall_status = "PASS"
        overall_class = "E0"
        overall_reason = "All required device classes are covered."

    report = {
        "milestone": 18,
        "profile": "device_class_expansion",
        "status": overall_status,
        "classification": overall_class,
        "reason": overall_reason,
        "required_device_classes": REQUIRED_DEVICE_CLASSES,
        "device_matrix": matrix_rows,
        "hosts": hosts,
        "meta": _runtime_meta(),
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "repro-classification.json").write_text(
        json.dumps(
            {
                "milestone": 18,
                "profile": "device_class_expansion",
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
    (out_dir / "device-matrix.json").write_text(
        json.dumps({"device_matrix": matrix_rows}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "pair-matrix.json").write_text(
        json.dumps(
            {
                "pairs": [
                    {
                        "pair": "device_class_coverage",
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
                "milestone": 18,
                "host_count": len(hosts),
                "required_device_classes": REQUIRED_DEVICE_CLASSES,
                "covered_device_classes": sorted([r["device_class"] for r in matrix_rows if r["status"] == "PASS"]),
                "status": overall_status,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (out_dir / "os-matrix.json").write_text(
        json.dumps(
            {
                "os_families": sorted({str(h.get("os_family", "")) for h in hosts}),
                "hosts": [
                    {
                        "host_id": h.get("host_id", ""),
                        "os_family": h.get("os_family", ""),
                        "arch": h.get("arch", ""),
                    }
                    for h in hosts
                ],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (out_dir / "language-matrix.json").write_text(
        json.dumps(
            {
                "languages_observed": ["python"],
                "note": (
                    "Milestone 18 focuses on device classes; expanded language coverage is validated in milestone 20."
                ),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (out_dir / "library-matrix.json").write_text(
        json.dumps(
            {
                "libraries_observed": sorted(
                    {
                        lib
                        for h in hosts
                        for lib, meta in h.get("frameworks", {}).items()
                        if isinstance(meta, dict) and bool(meta.get("present"))
                    }
                ),
                "note": "Milestone 18 captures visibility only; full library universality is milestone 21.",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    gaps = ["# Portability Gaps (Milestone 18)", ""]
    if missing:
        for cls in missing:
            gaps.append(f"- Missing `{cls}`: add host manifest + closure date in ADR.")
    else:
        gaps.append("- No portability gaps in required device classes.")
    (out_dir / "portability-gaps.md").write_text("\n".join(gaps) + "\n", encoding="utf-8")

    waivers: list[dict[str, Any]] = []
    if (ROOT / WAIVER_ADR).exists():
        waivers.append(
            {
                "id": "M12_TEMP_RESOURCE_GAP",
                "adr": WAIVER_ADR,
                "scope": "Milestones 13-15 execution unblocked while Milestone 12 is BLOCKED.",
                "status": "ACTIVE",
            }
        )
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
                "# Milestone 18: Device-Class Expansion Matrix",
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
        "# Known Limitations (Milestone 18)\n\n"
        "- Device-class detection is capability-driven and may need host-specific tooling "
        "(nvidia-smi/rocminfo/sycl-ls).\n"
        "- Full OS and language universality is covered by milestones 19 and 20.\n",
        encoding="utf-8",
    )
    (out_dir / "milestone.json").write_text(
        json.dumps(
            {
                "milestone": 18,
                "slug": "device-class-expansion",
                "owner": "Astrocytech/Glyphser",
                "target_date": "2026-09-15",
                "dependencies": [17, "17A"],
                "profiles": ["device_matrix"],
                "result": overall_status,
                "classification": overall_class,
                "evidence_dir": "evidence/repro/milestone-18-device-class-expansion/",
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
