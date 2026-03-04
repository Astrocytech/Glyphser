#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path
from typing import Any

from runtime.glyphser.model.model_ir_executor import execute
from tooling.lib.path_config import fixtures_root

ROOT = Path(__file__).resolve().parents[3]


def _load_dataset(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _allclose(a: Any, b: Any, abs_tol: float, rel_tol: float) -> bool:
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        diff = abs(float(a) - float(b))
        scale = max(abs(float(a)), abs(float(b)), 1.0)
        return diff <= max(abs_tol, rel_tol * scale)
    if isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        return all(_allclose(x, y, abs_tol, rel_tol) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict) and set(a.keys()) == set(b.keys()):
        return all(_allclose(a[k], b[k], abs_tol, rel_tol) for k in a.keys())
    return a == b


def _run_profile(driver_id: str, model_ir: dict[str, Any], inputs: list[float]) -> dict[str, Any]:
    return execute(
        {
            "ir_dag": model_ir,
            "input_data": {"input": inputs},
            "driver_id": driver_id,
            "mode": "forward",
            "replay_token": "milestone-3-pytorch-cpu-gpu",
            "tmmu_context": {"arena_config": {"default": {"capacity_bytes": 1_000_000, "alignment_bytes": 64}}},
        }
    )


def _torch_meta() -> dict[str, Any]:
    try:
        import torch
    except Exception as exc:  # pragma: no cover
        return {"torch_present": False, "error": str(exc)}

    meta: dict[str, Any] = {
        "torch_present": True,
        "torch_version": torch.__version__,
        "cuda_available": bool(torch.cuda.is_available()),
        "torch_cuda_version": getattr(torch.version, "cuda", None),
    }
    if meta["cuda_available"]:
        try:
            meta["gpu_model"] = torch.cuda.get_device_name(0)
        except Exception as exc:  # pragma: no cover
            meta["gpu_model_error"] = str(exc)
    return meta


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare PyTorch CPU and GPU reproducibility for Glyphser.")
    parser.add_argument("--abs-tol", type=float, default=1e-6)
    parser.add_argument("--rel-tol", type=float, default=1e-6)
    parser.add_argument(
        "--output-dir",
        default=str(ROOT / "evidence" / "repro" / "milestone-3-pytorch-cpu-gpu"),
        help="Directory to write report artifacts.",
    )
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    fixtures = fixtures_root() / "hello-core"
    dataset_path = fixtures / "tiny_synth_dataset.jsonl"
    model_ir_path = fixtures / "model_ir.json"
    dataset = _load_dataset(dataset_path)
    model_ir = json.loads(model_ir_path.read_text(encoding="utf-8"))
    inputs = dataset[0]["x"]

    cpu_result = _run_profile("pytorch_cpu", model_ir, inputs)
    gpu_result = _run_profile("pytorch_gpu", model_ir, inputs)

    meta = {
        "platform": platform.platform(),
        "kernel": platform.release(),
        "python": sys.version.split()[0],
        "torch": _torch_meta(),
        "abs_tol": args.abs_tol,
        "rel_tol": args.rel_tol,
    }

    status = "PASS"
    classification = "E0"
    reason = "CPU and GPU outputs/execution fingerprints match exactly."

    if "error" in cpu_result:
        status = "FAIL"
        classification = "E2"
        reason = f"CPU profile failed: {cpu_result['error']['code_id']}"
    elif "error" in gpu_result:
        status = "BLOCKED"
        classification = "E2"
        reason = f"GPU profile unavailable/failing: {gpu_result['error']['code_id']}"
    else:
        cpu_outputs = cpu_result.get("outputs")
        gpu_outputs = gpu_result.get("outputs")
        same_outputs = cpu_outputs == gpu_outputs
        same_fp = cpu_result.get("execution_fp") == gpu_result.get("execution_fp")
        if same_outputs and same_fp:
            status = "PASS"
            classification = "E0"
        elif _allclose(cpu_outputs, gpu_outputs, args.abs_tol, args.rel_tol):
            status = "PASS"
            classification = "E1"
            reason = "CPU/GPU outputs within configured tolerance."
        else:
            status = "FAIL"
            classification = "E2"
            reason = "CPU/GPU outputs diverge beyond tolerance."

    report = {
        "milestone": 3,
        "profile": "pytorch_cpu_gpu",
        "status": status,
        "classification": classification,
        "reason": reason,
        "cpu_result": cpu_result,
        "gpu_result": gpu_result,
        "meta": meta,
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    repro_classification = {
        "milestone": 3,
        "profile": "pytorch_cpu_gpu",
        "classification": classification,
        "status": status,
        "reason": reason,
        "abs_tol": args.abs_tol,
        "rel_tol": args.rel_tol,
        "excluded_operators": [],
    }
    (out_dir / "repro-classification.json").write_text(
        json.dumps(repro_classification, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "env-matrix.json").write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    conformance_hashes: dict[str, Any] = {"status": status}
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

    summary_lines = [
        "# Milestone 3: PyTorch CPU + GPU Reproducibility",
        "",
        f"Status: {status}",
        f"Classification: {classification}",
        f"Reason: {reason}",
        "",
        "## Command",
        f"`{Path(__file__).relative_to(ROOT)}`",
        "",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
    (out_dir / "known-limitations.md").write_text(
        "# Known Limitations (Milestone 3)\n\n- Scope is limited to hello-core and locked initial operator subset.\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {"status": status, "classification": classification, "reason": reason},
            indent=2,
            sort_keys=True,
        )
    )
    if status == "PASS":
        return 0
    if status == "BLOCKED":
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
