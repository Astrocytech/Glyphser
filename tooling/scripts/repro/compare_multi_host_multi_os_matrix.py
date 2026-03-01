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


MANDATORY_PROFILES = ["pytorch_cpu", "pytorch_gpu", "keras_cpu", "keras_gpu", "java_cpu"]


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run(cmd: list[str]) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except FileNotFoundError as exc:
        # Some host tools (for example nvidia-smi/lscpu/java) may not exist on every OS.
        return 127, "", str(exc)


def _parse_gpu_models() -> list[str]:
    code, out, _ = _run(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"])
    if code != 0 or not out:
        return []
    return [line.strip() for line in out.splitlines() if line.strip()]


def _profile_status_local() -> dict[str, str]:
    status = {
        "pytorch_cpu": "BLOCKED",
        "pytorch_gpu": "BLOCKED",
        "keras_cpu": "BLOCKED",
        "keras_gpu": "BLOCKED",
        "java_cpu": "BLOCKED",
    }

    try:
        import torch

        status["pytorch_cpu"] = "PASS"
        if torch.cuda.is_available():
            status["pytorch_gpu"] = "PASS"
    except Exception:
        pass

    try:
        import tensorflow as tf

        status["keras_cpu"] = "PASS"
        if tf.config.list_physical_devices("GPU"):
            status["keras_gpu"] = "PASS"
    except Exception:
        pass

    j_code, _, _ = _run(["java", "-version"])
    jc_code, _, _ = _run(["javac", "-version"])
    if j_code == 0 and jc_code == 0:
        status["java_cpu"] = "PASS"

    return status


def _collect_local_manifest() -> dict[str, Any]:
    py = sys.version.split()[0]
    os_family = platform.system()
    gpu_models = _parse_gpu_models()

    code, lscpu_out, _ = _run(["lscpu"])
    cpu_model = platform.processor() or platform.machine()
    if code == 0:
        for line in lscpu_out.splitlines():
            if line.lower().startswith("model name:"):
                cpu_model = line.split(":", 1)[1].strip()
                break

    java_code, java_out, java_err = _run(["java", "-version"])
    javac_code, javac_out, javac_err = _run(["javac", "-version"])

    torch_meta: dict[str, Any] = {"present": False}
    tf_meta: dict[str, Any] = {"present": False}
    try:
        import torch

        torch_meta = {
            "present": True,
            "version": torch.__version__,
            "cuda_available": bool(torch.cuda.is_available()),
            "cuda_version": getattr(torch.version, "cuda", None),
        }
        if torch.cuda.is_available():
            torch_meta["gpu_name"] = torch.cuda.get_device_name(0)
    except Exception as exc:
        torch_meta = {"present": False, "error": str(exc)}

    try:
        import tensorflow as tf

        gpus = tf.config.list_physical_devices("GPU")
        tf_meta = {
            "present": True,
            "version": tf.__version__,
            "gpu_visible": bool(gpus),
            "gpu_devices": [str(g) for g in gpus],
        }
    except Exception as exc:
        tf_meta = {"present": False, "error": str(exc)}

    return {
        "host_id": socket.gethostname(),
        "source": "local",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "os_family": os_family,
        "platform": platform.platform(),
        "kernel": platform.release(),
        "python": py,
        "cpu_model": cpu_model,
        "gpu_models": gpu_models,
        "profiles": _profile_status_local(),
        "frameworks": {
            "torch": torch_meta,
            "tensorflow": tf_meta,
            "java": {
                "java_ok": java_code == 0,
                "javac_ok": javac_code == 0,
                "java_version": java_err or java_out,
                "javac_version": javac_err or javac_out,
            },
        },
    }


def _load_manifest(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_host_profiles(host: dict[str, Any]) -> tuple[list[dict[str, Any]], bool]:
    rows: list[dict[str, Any]] = []
    ok = True

    profiles = host.get("profiles", {})
    gpu_capable = bool(host.get("gpu_models"))

    required = ["pytorch_cpu", "keras_cpu", "java_cpu"]
    if gpu_capable:
        required += ["pytorch_gpu", "keras_gpu"]

    for prof in required:
        st = profiles.get(prof, "BLOCKED")
        if st != "PASS":
            ok = False
        rows.append(
            {
                "host_id": host.get("host_id", "unknown"),
                "profile": prof,
                "status": st,
                "classification": "E0" if st == "PASS" else "E2",
                "reason": "profile validated" if st == "PASS" else "required profile missing or blocked",
            }
        )

    return rows, ok


def _is_windows(host: dict[str, Any]) -> bool:
    return str(host.get("os_family", "")).lower().startswith("windows")


def _is_linux(host: dict[str, Any]) -> bool:
    return str(host.get("os_family", "")).lower().startswith("linux")


def _has_gpu_model(hosts: list[dict[str, Any]], pattern: str) -> bool:
    rgx = re.compile(pattern, re.IGNORECASE)
    for host in hosts:
        for g in host.get("gpu_models", []):
            if rgx.search(g):
                return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Milestone 12 multi-host/multi-OS reproducibility matrix.")
    parser.add_argument(
        "--host-manifest",
        action="append",
        default=[],
        help="Additional host manifest JSON file(s) from other machines/OS profiles.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(ROOT / "evidence" / "repro" / "milestone-12-multi-host-multi-os"),
    )
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    local_host = _collect_local_manifest()
    local_manifest_path = out_dir / f"host-{local_host['host_id']}.json"
    local_manifest_path.write_text(json.dumps(local_host, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    hosts = [local_host]
    for p in args.host_manifest:
        path = Path(p)
        if not path.is_absolute():
            path = ROOT / path
        hosts.append(_load_manifest(path))

    matrix_rows: list[dict[str, Any]] = []
    all_hosts_profile_ok = True
    for host in hosts:
        rows, ok = _validate_host_profiles(host)
        matrix_rows.extend(rows)
        all_hosts_profile_ok = all_hosts_profile_ok and ok

    linux_hosts = sum(1 for h in hosts if _is_linux(h))
    windows_hosts = sum(1 for h in hosts if _is_windows(h))
    unique_gpu_models = sorted({g for h in hosts for g in h.get("gpu_models", [])})

    constraints = {
        "linux_hosts_required": 2,
        "windows_hosts_required": 1,
        "gpu_arch_required": 2,
        "linux_hosts_observed": linux_hosts,
        "windows_hosts_observed": windows_hosts,
        "gpu_models_observed": unique_gpu_models,
        "gpu_model_count_observed": len(unique_gpu_models),
        "baseline_gpu_present": _has_gpu_model(hosts, r"GTX\s*1070"),
        "newer_gpu_present": _has_gpu_model(hosts, r"RTX\s*(30|40|50)"),
    }

    requirements_ok = (
        linux_hosts >= 2
        and windows_hosts >= 1
        and len(unique_gpu_models) >= 2
        and constraints["baseline_gpu_present"]
        and constraints["newer_gpu_present"]
    )

    if requirements_ok and all_hosts_profile_ok:
        overall_status = "PASS"
        overall_class = "E1"
        overall_reason = "Multi-host, multi-OS, and heterogeneous GPU matrix requirements satisfied."
    else:
        overall_status = "BLOCKED"
        overall_class = "E2"
        missing: list[str] = []
        if linux_hosts < 2:
            missing.append("need >=2 Linux hosts")
        if windows_hosts < 1:
            missing.append("need >=1 Windows host")
        if len(unique_gpu_models) < 2:
            missing.append("need >=2 GPU architectures")
        if not constraints["baseline_gpu_present"]:
            missing.append("missing GTX 1070 baseline host")
        if not constraints["newer_gpu_present"]:
            missing.append("missing RTX 30+ host")
        if not all_hosts_profile_ok:
            missing.append("one or more required profile cells are non-PASS")
        overall_reason = "; ".join(missing) if missing else "matrix requirements not satisfied"

    report = {
        "milestone": 12,
        "profile": "multi_host_multi_os_matrix",
        "status": overall_status,
        "classification": overall_class,
        "reason": overall_reason,
        "hosts": hosts,
        "host_count": len(hosts),
        "matrix_rows": matrix_rows,
        "constraints": constraints,
        "meta": {
            "timestamp_utc": datetime.now(UTC).isoformat(),
            "cwd": str(ROOT),
        },
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    repro = {
        "milestone": 12,
        "profile": "multi_host_multi_os_matrix",
        "status": overall_status,
        "classification": overall_class,
        "reason": overall_reason,
        "excluded_operators": [],
    }
    (out_dir / "repro-classification.json").write_text(json.dumps(repro, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "pair-matrix.json").write_text(json.dumps({"pairs": matrix_rows}, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    coverage = {
        "milestone": 12,
        "status": overall_status,
        "host_count": len(hosts),
        "linux_hosts": linux_hosts,
        "windows_hosts": windows_hosts,
        "gpu_models": unique_gpu_models,
        "profiles": MANDATORY_PROFILES,
        "mandatory_profiles": MANDATORY_PROFILES,
        "constraints": constraints,
    }
    (out_dir / "coverage-summary.json").write_text(json.dumps(coverage, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "waivers.json").write_text(json.dumps({"waivers": []}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "env-matrix.json").write_text(json.dumps({"hosts": hosts, "constraints": constraints}, indent=2, sort_keys=True) + "\n", encoding="utf-8")

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
    (out_dir / "conformance-hashes.json").write_text(json.dumps(conformance_hashes, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    summary = [
        "# Milestone 12: Multi-Host and Multi-OS Matrix",
        "",
        f"Status: {overall_status}",
        f"Classification: {overall_class}",
        f"Reason: {overall_reason}",
        "",
        f"Hosts observed: {len(hosts)}",
        f"Linux hosts: {linux_hosts}",
        f"Windows hosts: {windows_hosts}",
        f"GPU models: {', '.join(unique_gpu_models) if unique_gpu_models else 'none'}",
        "",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary), encoding="utf-8")
    (out_dir / "known-limitations.md").write_text(
        "# Known Limitations (Milestone 12)\n\n"
        "- Pass requires external host manifests for additional Linux/Windows nodes and second GPU architecture.\n",
        encoding="utf-8",
    )

    manifest = {
        "milestone": 12,
        "slug": "multi-host-multi-os",
        "owner": "Astrocytech/Glyphser",
        "target_date": "2026-05-10",
        "dependencies": [11],
        "profiles": MANDATORY_PROFILES,
        "result": overall_status,
        "classification": overall_class,
        "evidence_dir": "evidence/repro/milestone-12-multi-host-multi-os/",
        "host_manifests": [str(local_manifest_path.relative_to(ROOT))] + args.host_manifest,
    }
    (out_dir / "milestone.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({"status": overall_status, "classification": overall_class, "reason": overall_reason}, indent=2, sort_keys=True))
    return 0 if overall_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
