#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import shlex
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from runtime.glyphser.model.model_ir_executor import execute
from tooling.lib.path_config import fixtures_root

ROOT = Path(__file__).resolve().parents[3]


WAIVER_ADRS = [
    "evidence/repro/decisions/ADR-2026-03-01-m12-resource-gap-temporary-waiver.md",
    "evidence/repro/decisions/ADR-2026-03-01-m18-device-resource-gap-temporary-waiver.md",
    "evidence/repro/decisions/ADR-2026-03-01-m19-proceed-under-m18-waiver.md",
    "evidence/repro/decisions/ADR-2026-03-01-m20-proceed-under-m19-pause.md",
]


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


def _run_cmd(cmd: str, inputs: list[float], weights: list[float], bias: float) -> dict[str, Any]:
    rendered = (
        cmd.replace("{input_csv}", ",".join(str(x) for x in inputs))
        .replace("{weights_csv}", ",".join(str(x) for x in weights))
        .replace("{bias}", str(bias))
    )
    try:
        argv = shlex.split(rendered)
    except Exception as exc:
        return {"error": {"code_id": "BAD_COMMAND", "message": str(exc)}}
    try:
        proc = subprocess.run(argv, capture_output=True, text=True, cwd=str(ROOT))
    except FileNotFoundError as exc:
        return {"error": {"code_id": "RUNTIME_EXEC_ERROR", "message": str(exc)}}
    if proc.returncode != 0:
        return {
            "error": {
                "code_id": "RUNTIME_EXEC_ERROR",
                "message": proc.stderr.strip() or proc.stdout.strip() or f"code={proc.returncode}",
            }
        }
    try:
        payload = json.loads(proc.stdout.strip())
    except Exception as exc:
        return {"error": {"code_id": "OUTPUT_PARSE_ERROR", "message": str(exc)}}
    return {
        "outputs": payload.get("outputs"),
        "execution_fp": hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest(),
        "runtime": payload.get("runtime", "external"),
    }


def _run_pytorch_cpu(model_ir: dict[str, Any], inputs: list[float]) -> dict[str, Any]:
    return execute(
        {
            "ir_dag": model_ir,
            "input_data": {"input": inputs},
            "driver_id": "pytorch_cpu",
            "mode": "forward",
            "replay_token": "milestone-21-library-ecosystem",
            "tmmu_context": {"arena_config": {"default": {"capacity_bytes": 1_000_000, "alignment_bytes": 64}}},
        }
    )


def _run_keras_cpu(model_ir: dict[str, Any], inputs: list[float]) -> dict[str, Any]:
    return execute(
        {
            "ir_dag": model_ir,
            "input_data": {"input": inputs},
            "driver_id": "keras_cpu",
            "mode": "forward",
            "replay_token": "milestone-21-library-ecosystem",
            "tmmu_context": {"arena_config": {"default": {"capacity_bytes": 1_000_000, "alignment_bytes": 64}}},
        }
    )


def _run_jax(inputs: list[float], weights: list[float], bias: float) -> dict[str, Any]:
    try:
        import jax.numpy as jnp
    except Exception as exc:
        return {"error": {"code_id": "LIBRARY_MISSING", "message": str(exc)}}
    x = jnp.array(inputs, dtype=jnp.float64)
    w = jnp.array(weights, dtype=jnp.float64)
    b = jnp.array(bias, dtype=jnp.float64)
    out = jnp.dot(x, w) + b
    py_out = [[float(out)]]
    payload = {"runtime": "jax_cpu", "outputs": py_out}
    return {
        "outputs": py_out,
        "execution_fp": hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest(),
        "runtime": "jax_cpu",
    }


def _run_onnxruntime(inputs: list[float], weights: list[float], bias: float) -> dict[str, Any]:
    try:
        import numpy as np
        import onnx
        import onnxruntime as ort
        from onnx import TensorProto, helper
    except Exception as exc:
        return {"error": {"code_id": "LIBRARY_MISSING", "message": str(exc)}}
    dim = len(inputs)
    node = helper.make_node("Gemm", inputs=["X", "W", "B"], outputs=["Y"], alpha=1.0, beta=1.0, transB=0)
    graph = helper.make_graph(
        [node],
        "dense_graph",
        inputs=[helper.make_tensor_value_info("X", TensorProto.DOUBLE, [1, dim])],
        outputs=[helper.make_tensor_value_info("Y", TensorProto.DOUBLE, [1, 1])],
        initializer=[
            helper.make_tensor("W", TensorProto.DOUBLE, [dim, 1], [float(v) for v in weights]),
            helper.make_tensor("B", TensorProto.DOUBLE, [1], [float(bias)]),
        ],
    )
    model = helper.make_model(graph, producer_name="glyphser-m21")
    onnx.checker.check_model(model)
    sess = ort.InferenceSession(model.SerializeToString(), providers=["CPUExecutionProvider"])
    x = np.array([inputs], dtype=np.float64)
    y = sess.run(None, {"X": x})[0]
    py_out = [[float(y[0][0])]]
    payload = {"runtime": "onnxruntime_cpu", "outputs": py_out}
    return {
        "outputs": py_out,
        "execution_fp": hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest(),
        "runtime": "onnxruntime_cpu",
    }


def _runtime_meta() -> dict[str, Any]:
    meta: dict[str, Any] = {
        "platform": platform.platform(),
        "kernel": platform.release(),
        "python": platform.python_version(),
        "timestamp_utc": datetime.now(UTC).isoformat(),
    }
    for pkg in ("jax", "onnxruntime", "onnx", "openvino", "tensorrt"):
        try:
            mod = __import__(pkg)
            meta[pkg] = {
                "present": True,
                "version": getattr(mod, "__version__", "unknown"),
            }
        except Exception as exc:
            meta[pkg] = {"present": False, "error": str(exc)}
    return meta


def main() -> int:
    parser = argparse.ArgumentParser(description="Milestone 21 library/runtime ecosystem expansion.")
    parser.add_argument("--abs-tol", type=float, default=1e-6)
    parser.add_argument("--rel-tol", type=float, default=1e-6)
    parser.add_argument(
        "--ovtrt-cmd",
        default="",
        help="Optional OpenVINO/TensorRT external command template with {input_csv} {weights_csv} {bias}.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(ROOT / "evidence" / "repro" / "milestone-21-library-ecosystem"),
    )
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    fixtures = fixtures_root() / "hello-core"
    dataset = [
        json.loads(line)
        for line in (fixtures / "tiny_synth_dataset.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    model_ir = json.loads((fixtures / "model_ir.json").read_text(encoding="utf-8"))
    inputs = dataset[0]["x"]
    dense = next(n for n in model_ir["nodes"] if n.get("instr") == "Dense")
    weights = dense["params"]["weights"]
    bias = float(dense["params"]["bias"])

    results = {
        "python_pytorch_cpu": _run_pytorch_cpu(model_ir, inputs),
        "python_keras_cpu": _run_keras_cpu(model_ir, inputs),
        "jax_cpu": _run_jax(inputs, weights, bias),
        "onnxruntime_cpu": _run_onnxruntime(inputs, weights, bias),
        "openvino_tensorrt": (
            _run_cmd(args.ovtrt_cmd, inputs, weights, bias)
            if args.ovtrt_cmd.strip()
            else {
                "error": {
                    "code_id": "LIBRARY_NOT_CONFIGURED",
                    "message": "set --ovtrt-cmd for OpenVINO/TensorRT lane",
                }
            }
        ),
    }

    baseline = results["python_pytorch_cpu"]
    pair_rows = []
    library_rows = []
    for lane, out in results.items():
        if lane == "python_pytorch_cpu":
            library_rows.append({"library_lane": lane, "status": "PASS"})
            continue
        if "error" in baseline or "error" in out:
            pair_rows.append(
                {
                    "pair": f"python_pytorch_cpu__vs__{lane}",
                    "status": "BLOCKED",
                    "classification": "E2",
                    "reason": "runtime error",
                    "a_result": baseline,
                    "b_result": out,
                }
            )
            library_rows.append({"library_lane": lane, "status": "BLOCKED"})
            continue
        if baseline.get("outputs") == out.get("outputs") and baseline.get("execution_fp") == out.get("execution_fp"):
            status, cls, reason = (
                "PASS",
                "E0",
                "Exact output and execution fingerprint match.",
            )
        elif _allclose(baseline.get("outputs"), out.get("outputs"), args.abs_tol, args.rel_tol):
            status, cls, reason = "PASS", "E1", "Outputs within tolerance."
        else:
            status, cls, reason = "FAIL", "E2", "Outputs diverge."
        pair_rows.append(
            {
                "pair": f"python_pytorch_cpu__vs__{lane}",
                "status": status,
                "classification": cls,
                "reason": reason,
                "a_result": baseline,
                "b_result": out,
            }
        )
        library_rows.append({"library_lane": lane, "status": status})

    statuses = [r["status"] for r in pair_rows]
    if any(s == "FAIL" for s in statuses):
        overall_status, overall_class, overall_reason = (
            "FAIL",
            "E2",
            "At least one library lane failed.",
        )
    elif any(s == "BLOCKED" for s in statuses):
        overall_status, overall_class, overall_reason = (
            "BLOCKED",
            "E2",
            "At least one library lane is blocked.",
        )
    else:
        overall_status = "PASS"
        overall_class = "E0" if all(r["classification"] == "E0" for r in pair_rows) else "E1"
        overall_reason = "All library lanes pass."

    report = {
        "milestone": 21,
        "profile": "library_ecosystem",
        "status": overall_status,
        "classification": overall_class,
        "reason": overall_reason,
        "results": results,
        "pairs": pair_rows,
        "library_matrix": library_rows,
        "meta": {"abs_tol": args.abs_tol, "rel_tol": args.rel_tol, **_runtime_meta()},
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "repro-classification.json").write_text(
        json.dumps(
            {
                "milestone": 21,
                "profile": "library_ecosystem",
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
        json.dumps({"pairs": pair_rows}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "library-matrix.json").write_text(
        json.dumps({"library_matrix": library_rows}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "env-matrix.json").write_text(
        json.dumps(report["meta"], indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (out_dir / "coverage-summary.json").write_text(
        json.dumps(
            {"milestone": 21, "lane_count": len(results), "status": overall_status},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (out_dir / "device-matrix.json").write_text(
        json.dumps(
            {"note": "Milestone 21 focuses on runtime/library lanes."},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (out_dir / "os-matrix.json").write_text(
        json.dumps(
            {"note": "Milestone 21 focuses on runtime/library lanes."},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (out_dir / "language-matrix.json").write_text(
        json.dumps(
            {"note": "Milestone 21 follows language expansion from milestone 20."},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (out_dir / "portability-gaps.md").write_text(
        "# Portability Gaps (Milestone 21)\n\n"
        + "\n".join(
            f"- `{lane}` blocked: {res['error']['message']}"
            for lane, res in results.items()
            if isinstance(res, dict) and "error" in res
        )
        + "\n",
        encoding="utf-8",
    )
    waivers = []
    for adr in WAIVER_ADRS:
        if (ROOT / adr).exists():
            waivers.append({"adr": adr, "status": "ACTIVE"})
    (out_dir / "waivers.json").write_text(
        json.dumps({"waivers": waivers}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    conformance_hashes: dict[str, Any] = {"status": overall_status}
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
                "# Milestone 21: Library and Runtime Ecosystem Expansion",
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
        "# Known Limitations (Milestone 21)\n\n"
        "- OpenVINO/TensorRT lane is external-command based (`--ovtrt-cmd`) to keep runtime portability.\n"
        "- ONNX Runtime lane requires `onnxruntime` + `onnx` + `numpy` python packages.\n",
        encoding="utf-8",
    )
    (out_dir / "milestone.json").write_text(
        json.dumps(
            {
                "milestone": 21,
                "slug": "library-ecosystem",
                "owner": "Astrocytech/Glyphser",
                "target_date": "2026-11-12",
                "dependencies": [20],
                "profiles": list(results.keys()),
                "result": overall_status,
                "classification": overall_class,
                "evidence_dir": "evidence/repro/milestone-21-library-ecosystem/",
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
