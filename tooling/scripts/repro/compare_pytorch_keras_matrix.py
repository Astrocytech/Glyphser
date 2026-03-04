#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from runtime.glyphser.model.model_ir_executor import execute
from tooling.lib.path_config import fixtures_root

PAIRS: list[tuple[str, str]] = [
    ("pytorch_cpu", "keras_cpu"),
    ("pytorch_cpu", "keras_gpu"),
    ("pytorch_gpu", "keras_cpu"),
    ("pytorch_gpu", "keras_gpu"),
]


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
            "replay_token": "milestone-7-pytorch-keras-matrix",
            "tmmu_context": {"arena_config": {"default": {"capacity_bytes": 1_000_000, "alignment_bytes": 64}}},
        }
    )


def _runtime_meta() -> dict[str, Any]:
    meta: dict[str, Any] = {
        "platform": platform.platform(),
        "kernel": platform.release(),
        "python": sys.version.split()[0],
    }

    try:
        import torch

        meta["torch"] = {
            "version": torch.__version__,
            "cuda_available": bool(torch.cuda.is_available()),
            "cuda_version": getattr(torch.version, "cuda", None),
        }
        if torch.cuda.is_available():
            meta["torch"]["gpu_name"] = torch.cuda.get_device_name(0)
    except Exception as exc:  # pragma: no cover
        meta["torch"] = {"present": False, "error": str(exc)}

    try:
        import tensorflow as tf

        gpus = tf.config.list_physical_devices("GPU")
        meta["tensorflow"] = {
            "version": tf.__version__,
            "gpu_visible": bool(gpus),
            "gpu_devices": [str(g) for g in gpus],
        }
    except Exception as exc:  # pragma: no cover
        meta["tensorflow"] = {"present": False, "error": str(exc)}

    return meta


def _classify_pair(
    a_id: str,
    b_id: str,
    a_res: dict[str, Any],
    b_res: dict[str, Any],
    abs_tol: float,
    rel_tol: float,
) -> dict[str, Any]:
    if "error" in a_res:
        return {
            "pair": f"{a_id}__vs__{b_id}",
            "status": "BLOCKED",
            "classification": "E2",
            "reason": f"{a_id} failed: {a_res['error']['code_id']}",
            "a_result": a_res,
            "b_result": b_res,
        }
    if "error" in b_res:
        return {
            "pair": f"{a_id}__vs__{b_id}",
            "status": "BLOCKED",
            "classification": "E2",
            "reason": f"{b_id} failed: {b_res['error']['code_id']}",
            "a_result": a_res,
            "b_result": b_res,
        }

    same_outputs = a_res.get("outputs") == b_res.get("outputs")
    same_fp = a_res.get("execution_fp") == b_res.get("execution_fp")
    if same_outputs and same_fp:
        return {
            "pair": f"{a_id}__vs__{b_id}",
            "status": "PASS",
            "classification": "E0",
            "reason": "Exact output and execution fingerprint match.",
            "a_result": a_res,
            "b_result": b_res,
        }

    if _allclose(a_res.get("outputs"), b_res.get("outputs"), abs_tol, rel_tol):
        return {
            "pair": f"{a_id}__vs__{b_id}",
            "status": "PASS",
            "classification": "E1",
            "reason": "Outputs within configured tolerance.",
            "a_result": a_res,
            "b_result": b_res,
        }

    return {
        "pair": f"{a_id}__vs__{b_id}",
        "status": "FAIL",
        "classification": "E2",
        "reason": "Outputs diverge beyond tolerance.",
        "a_result": a_res,
        "b_result": b_res,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Milestone 7 cross-framework reproducibility matrix.")
    parser.add_argument("--abs-tol", type=float, default=1e-6)
    parser.add_argument("--rel-tol", type=float, default=1e-6)
    parser.add_argument(
        "--output-dir",
        default=str(ROOT / "evidence" / "repro" / "milestone-7-pytorch-keras"),
        help="Directory to write report artifacts.",
    )
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    fixtures = fixtures_root() / "hello-core"
    dataset = _load_dataset(fixtures / "tiny_synth_dataset.jsonl")
    model_ir = json.loads((fixtures / "model_ir.json").read_text(encoding="utf-8"))
    inputs = dataset[0]["x"]

    pair_results: list[dict[str, Any]] = []
    for a_id, b_id in PAIRS:
        a_res = _run_profile(a_id, model_ir, inputs)
        b_res = _run_profile(b_id, model_ir, inputs)
        pair_results.append(_classify_pair(a_id, b_id, a_res, b_res, args.abs_tol, args.rel_tol))

    statuses = [r["status"] for r in pair_results]
    if any(s == "FAIL" for s in statuses):
        overall_status = "FAIL"
        overall_class = "E2"
        overall_reason = "At least one cross-framework pair failed tolerance."
    elif any(s == "BLOCKED" for s in statuses):
        overall_status = "BLOCKED"
        overall_class = "E2"
        overall_reason = "At least one cross-framework pair is blocked by runtime visibility."
    else:
        classes = [r["classification"] for r in pair_results]
        overall_status = "PASS"
        overall_class = "E0" if all(c == "E0" for c in classes) else "E1"
        overall_reason = "All cross-framework pairs pass."

    report = {
        "milestone": 7,
        "profile": "pytorch_keras_cross_matrix",
        "status": overall_status,
        "classification": overall_class,
        "reason": overall_reason,
        "pairs": pair_results,
        "meta": {
            "abs_tol": args.abs_tol,
            "rel_tol": args.rel_tol,
            **_runtime_meta(),
        },
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    repro_classification = {
        "milestone": 7,
        "profile": "pytorch_keras_cross_matrix",
        "classification": overall_class,
        "status": overall_status,
        "reason": overall_reason,
        "abs_tol": args.abs_tol,
        "rel_tol": args.rel_tol,
        "excluded_operators": [],
    }
    (out_dir / "repro-classification.json").write_text(
        json.dumps(repro_classification, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "env-matrix.json").write_text(
        json.dumps(report["meta"], indent=2, sort_keys=True) + "\n", encoding="utf-8"
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

    summary_lines = [
        "# Milestone 7: PyTorch + Keras Cross-Combination Reproducibility",
        "",
        f"Status: {overall_status}",
        f"Classification: {overall_class}",
        f"Reason: {overall_reason}",
        "",
        "## Cross Pairs",
        "- pytorch_cpu vs keras_cpu",
        "- pytorch_cpu vs keras_gpu",
        "- pytorch_gpu vs keras_cpu",
        "- pytorch_gpu vs keras_gpu",
        "",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
    (out_dir / "known-limitations.md").write_text(
        "# Known Limitations (Milestone 7)\n\n- Current matrix uses hello-core and locked initial operator subset.\n",
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
    if overall_status == "PASS":
        return 0
    if overall_status == "BLOCKED":
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
