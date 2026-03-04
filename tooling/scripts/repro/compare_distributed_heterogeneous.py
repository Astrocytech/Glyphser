#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import random
import socket
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from runtime.glyphser.model.model_ir_executor import execute  # noqa: E402
from tooling.lib.path_config import fixtures_root  # noqa: E402

WAIVER_ADRS = [
    "evidence/repro/decisions/ADR-2026-03-01-m12-resource-gap-temporary-waiver.md",
    "evidence/repro/decisions/ADR-2026-03-01-m18-device-resource-gap-temporary-waiver.md",
    "evidence/repro/decisions/ADR-2026-03-01-m19-proceed-under-m18-waiver.md",
    "evidence/repro/decisions/ADR-2026-03-01-m23-progress-with-limited-cluster.md",
]


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run(cmd: list[str]) -> tuple[int, str, str]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except FileNotFoundError as exc:
        return 127, "", str(exc)


def _is_wsl() -> bool:
    if platform.system().lower() != "linux":
        return False
    rel = platform.release().lower()
    return "microsoft" in rel or "wsl" in rel


def _collect_local_host() -> dict[str, Any]:
    gpu = False
    code, out, _ = _run(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"])
    if code == 0 and out:
        gpu = True
    return {
        "host_id": socket.gethostname(),
        "source": "local",
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "os_family": platform.system(),
        "platform": platform.platform(),
        "kernel": platform.release(),
        "arch": platform.machine().lower(),
        "is_wsl": _is_wsl(),
        "gpu_present": gpu,
    }


def _load_host(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _runtime_meta() -> dict[str, Any]:
    return {
        "platform": platform.platform(),
        "kernel": platform.release(),
        "python": platform.python_version(),
        "timestamp_utc": datetime.now(UTC).isoformat(),
    }


def _run_profile(driver_id: str, model_ir: dict[str, Any], inputs: list[float], replay_token: str) -> dict[str, Any]:
    return execute(
        {
            "ir_dag": model_ir,
            "input_data": {"input": inputs},
            "driver_id": driver_id,
            "mode": "forward",
            "replay_token": replay_token,
            "tmmu_context": {"arena_config": {"default": {"capacity_bytes": 1_000_000, "alignment_bytes": 64}}},
        }
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Milestone 23 distributed heterogeneous reproducibility.")
    parser.add_argument(
        "--host-manifest",
        action="append",
        default=[],
        help="Additional host manifest json paths.",
    )
    parser.add_argument("--seed", type=int, default=1337)
    parser.add_argument(
        "--output-dir",
        default=str(ROOT / "evidence" / "repro" / "milestone-23-distributed-heterogeneous"),
    )
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    local = _collect_local_host()
    local_path = out_dir / f"host-{local['host_id']}.json"
    local_path.write_text(json.dumps(local, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    hosts = [local]
    for p in args.host_manifest:
        path = Path(p)
        if not path.is_absolute():
            path = ROOT / path
        hosts.append(_load_host(path))

    unique_os = sorted({str(h.get("os_family", "")) for h in hosts})
    unique_arch = sorted({str(h.get("arch", "")) for h in hosts})
    gpu_hosts = [h.get("host_id", "") for h in hosts if bool(h.get("gpu_present", False))]
    hetero_ok = len(hosts) >= 2 and (len(unique_os) >= 2 or len(unique_arch) >= 2)

    fixtures = fixtures_root() / "hello-core"
    dataset = [
        json.loads(line)
        for line in (fixtures / "tiny_synth_dataset.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    model_ir = json.loads((fixtures / "model_ir.json").read_text(encoding="utf-8"))
    inputs = dataset[0]["x"]

    # Simulate distributed perturbation by shuffling node processing schedule proxy (replay tokens and host ordering).
    rng = random.Random(args.seed)
    host_order_a = [h.get("host_id", "unknown") for h in hosts]
    host_order_b = host_order_a[:]
    rng.shuffle(host_order_b)

    base_cpu = _run_profile("pytorch_cpu", model_ir, inputs, replay_token=f"m23-a-{','.join(host_order_a)}")
    pert_cpu = _run_profile("pytorch_cpu", model_ir, inputs, replay_token=f"m23-b-{','.join(host_order_b)}")
    cpu_equal = base_cpu.get("outputs") == pert_cpu.get("outputs") and base_cpu.get("execution_fp") == pert_cpu.get(
        "execution_fp"
    )

    gpu_row: dict[str, Any]
    if gpu_hosts:
        base_gpu = _run_profile(
            "pytorch_gpu",
            model_ir,
            inputs,
            replay_token=f"m23-gpu-a-{','.join(host_order_a)}",
        )
        pert_gpu = _run_profile(
            "pytorch_gpu",
            model_ir,
            inputs,
            replay_token=f"m23-gpu-b-{','.join(host_order_b)}",
        )
        if "error" in base_gpu or "error" in pert_gpu:
            gpu_row = {
                "check": "gpu_perturbation_replay",
                "status": "BLOCKED",
                "classification": "E2",
                "reason": "GPU path unavailable in current runtime despite GPU host visibility.",
                "base": base_gpu,
                "perturbed": pert_gpu,
            }
        else:
            gpu_ok = base_gpu.get("outputs") == pert_gpu.get("outputs") and base_gpu.get(
                "execution_fp"
            ) == pert_gpu.get("execution_fp")
            gpu_row = {
                "check": "gpu_perturbation_replay",
                "status": "PASS" if gpu_ok else "FAIL",
                "classification": "E0" if gpu_ok else "E2",
                "reason": "GPU perturbation replay is deterministic."
                if gpu_ok
                else "GPU perturbation replay diverged.",
                "base": base_gpu,
                "perturbed": pert_gpu,
            }
    else:
        gpu_row = {
            "check": "gpu_perturbation_replay",
            "status": "BLOCKED",
            "classification": "E2",
            "reason": "No GPU host present in provided host manifests.",
        }

    checks = [
        {
            "check": "cluster_heterogeneity_coverage",
            "status": "PASS" if hetero_ok else "BLOCKED",
            "classification": "E0" if hetero_ok else "E2",
            "reason": "Host set is heterogeneous."
            if hetero_ok
            else "Need >=2 hosts with heterogeneous OS/arch coverage.",
            "details": {
                "host_count": len(hosts),
                "unique_os": unique_os,
                "unique_arch": unique_arch,
            },
        },
        {
            "check": "cpu_perturbation_replay",
            "status": "PASS" if cpu_equal else "FAIL",
            "classification": "E0" if cpu_equal else "E2",
            "reason": "CPU perturbation replay is deterministic." if cpu_equal else "CPU perturbation replay diverged.",
            "base": base_cpu,
            "perturbed": pert_cpu,
            "host_order_a": host_order_a,
            "host_order_b": host_order_b,
        },
        gpu_row,
    ]

    statuses = [c["status"] for c in checks]
    if any(s == "FAIL" for s in statuses):
        overall_status, overall_class, overall_reason = (
            "FAIL",
            "E2",
            "At least one distributed reproducibility check failed.",
        )
    elif any(s == "BLOCKED" for s in statuses):
        overall_status, overall_class, overall_reason = (
            "BLOCKED",
            "E2",
            "At least one distributed reproducibility check is blocked.",
        )
    else:
        overall_status, overall_class, overall_reason = (
            "PASS",
            "E0",
            "Distributed heterogeneous reproducibility checks pass.",
        )

    report = {
        "milestone": 23,
        "profile": "distributed_heterogeneous",
        "status": overall_status,
        "classification": overall_class,
        "reason": overall_reason,
        "hosts": hosts,
        "checks": checks,
        "meta": {"seed": args.seed, **_runtime_meta()},
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "repro-classification.json").write_text(
        json.dumps(
            {
                "milestone": 23,
                "profile": "distributed_heterogeneous",
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
            {
                "pairs": [
                    {
                        "pair": "distributed_cluster_replay",
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
                "milestone": 23,
                "host_count": len(hosts),
                "unique_os": unique_os,
                "unique_arch": unique_arch,
                "gpu_host_count": len(gpu_hosts),
                "status": overall_status,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (out_dir / "device-matrix.json").write_text(
        json.dumps({"gpu_hosts": gpu_hosts, "host_count": len(hosts)}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "os-matrix.json").write_text(
        json.dumps({"unique_os": unique_os, "host_count": len(hosts)}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "language-matrix.json").write_text(
        json.dumps(
            {"note": "Milestone 23 validates distributed replay behavior on existing language adapters."},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (out_dir / "library-matrix.json").write_text(
        json.dumps(
            {"note": "Milestone 23 focuses on cluster replay, not library expansion."},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    gaps = ["# Portability Gaps (Milestone 23)", ""]
    for c in checks:
        if c["status"] != "PASS":
            gaps.append(f"- `{c['check']}`: {c['reason']}")
    if len(gaps) == 2:
        gaps.append("- No portability gaps detected.")
    (out_dir / "portability-gaps.md").write_text("\n".join(gaps) + "\n", encoding="utf-8")
    waivers = []
    for adr in WAIVER_ADRS:
        if (ROOT / adr).exists():
            waivers.append({"adr": adr, "status": "ACTIVE"})
    (out_dir / "waivers.json").write_text(
        json.dumps({"waivers": waivers}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    conformance_hashes = {"status": overall_status}
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
    (out_dir / "conformance-hashes.json").write_text(
        json.dumps(conformance_hashes, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "summary.md").write_text(
        "\n".join(
            [
                "# Milestone 23: Distributed and Heterogeneous Cluster Reproducibility",
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
        "# Known Limitations (Milestone 23)\n\n"
        "- Full PASS requires heterogeneous multi-host manifests and at least one GPU host path.\n"
        "- Current harness simulates perturbation through deterministic host-order replay tokens.\n",
        encoding="utf-8",
    )
    (out_dir / "milestone.json").write_text(
        json.dumps(
            {
                "milestone": 23,
                "slug": "distributed-heterogeneous",
                "owner": "Astrocytech/Glyphser",
                "target_date": "2027-01-14",
                "dependencies": [22],
                "profiles": ["distributed_cluster"],
                "result": overall_status,
                "classification": overall_class,
                "evidence_dir": "evidence/repro/milestone-23-distributed-heterogeneous/",
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
