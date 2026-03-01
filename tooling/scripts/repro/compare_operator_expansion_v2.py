#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import platform
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from runtime.glyphser.model.model_ir_executor import execute  # noqa: E402

PROFILES: list[str] = ["pytorch_cpu", "pytorch_gpu", "keras_cpu", "keras_gpu", "java_cpu"]
NON_JAVA_PROFILES = ["pytorch_cpu", "pytorch_gpu", "keras_cpu", "keras_gpu"]
JAVA_SRC = ROOT / "tooling" / "scripts" / "repro" / "java_bridge" / "OperatorExpansionJavaRunner.java"
JAVA_DIR = JAVA_SRC.parent
JAVA_CLASS = "OperatorExpansionJavaRunner"
JAVA_CLASS_FILE = JAVA_DIR / f"{JAVA_CLASS}.class"


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
        return all(_allclose(a[k], b[k], abs_tol, rel_tol) for k in a)
    return a == b


def _csv(values: list[float]) -> str:
    return ",".join(str(v) for v in values)


def _flatten_2d(values: list[list[float]]) -> list[float]:
    return [x for row in values for x in row]


def _case_ir(op: str, params: dict[str, Any], shape_out: list[int], inputs: list[dict[str, Any]]) -> dict[str, Any]:
    nodes = [{"node_id": "x", "instr": "Input", "inputs": [], "shape_out": inputs[0]["shape_out"], "dtype": "float64"}]
    for idx in range(1, len(inputs)):
        nodes.append(
            {
                "node_id": f"x{idx+1}",
                "instr": "Input",
                "inputs": [],
                "shape_out": inputs[idx]["shape_out"],
                "dtype": "float64",
            }
        )

    op_inputs: list[dict[str, Any]] = [{"node_id": "x", "output_idx": 0}]
    for idx in range(1, len(inputs)):
        op_inputs.append({"node_id": f"x{idx+1}", "output_idx": 0})

    nodes.append(
        {
            "node_id": "op",
            "instr": op,
            "inputs": op_inputs,
            "shape_out": shape_out,
            "dtype": "float64",
            "params": params,
        }
    )
    nodes.append(
        {
            "node_id": "out",
            "instr": "Output",
            "inputs": [{"node_id": "op", "output_idx": 0}],
            "shape_out": shape_out,
            "dtype": "float64",
        }
    )

    return {
        "ir_schema_hash": "sha256:milestone9-operator-expansion-v2",
        "nodes": nodes,
        "outputs": [{"node_id": "out", "output_idx": 0}],
    }


CASES: list[dict[str, Any]] = [
    {
        "case_id": "matmul_2x2",
        "family": "matmul_variants",
        "op": "MatMul",
        "shape_out": [2, 2],
        "params": {},
        "inputs": [
            {"key": "x", "shape_out": [2, 2], "value": [[1.0, 2.0], [3.0, 4.0]]},
            {"key": "x2", "shape_out": [2, 2], "value": [[0.5, 1.0], [1.5, -1.0]]},
        ],
    },
    {
        "case_id": "reduce_sum_vec4",
        "family": "reductions",
        "op": "ReduceSum",
        "shape_out": [1],
        "params": {},
        "inputs": [{"key": "x", "shape_out": [4], "value": [1.0, -2.0, 3.5, 0.5]}],
    },
    {
        "case_id": "reshape_4_to_2x2",
        "family": "reshape_transpose",
        "op": "Reshape",
        "shape_out": [2, 2],
        "params": {"shape": [2, 2]},
        "inputs": [{"key": "x", "shape_out": [4], "value": [1.0, 2.0, 3.0, 4.0]}],
    },
    {
        "case_id": "transpose_2x3_to_3x2",
        "family": "reshape_transpose",
        "op": "Transpose",
        "shape_out": [3, 2],
        "params": {"perm": [1, 0]},
        "inputs": [{"key": "x", "shape_out": [2, 3], "value": [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]}],
    },
    {
        "case_id": "softmax_vec3",
        "family": "softmax_loss",
        "op": "Softmax",
        "shape_out": [3],
        "params": {"axis": -1},
        "inputs": [{"key": "x", "shape_out": [3], "value": [1.0, 2.0, 3.0]}],
    },
    {
        "case_id": "layernorm_vec3",
        "family": "normalization",
        "op": "LayerNorm",
        "shape_out": [3],
        "params": {"eps": 1e-5, "gamma": [1.0, 0.9, 1.1], "beta": [0.1, -0.1, 0.2]},
        "inputs": [{"key": "x", "shape_out": [3], "value": [0.5, -1.0, 2.0]}],
    },
    {
        "case_id": "mse_loss_vec3",
        "family": "softmax_loss",
        "op": "MSELoss",
        "shape_out": [1],
        "params": {},
        "inputs": [
            {"key": "x", "shape_out": [3], "value": [0.1, 0.5, 0.9]},
            {"key": "x2", "shape_out": [3], "value": [0.0, 1.0, 0.8]},
        ],
    },
]


def _run_profile(profile: str, case: dict[str, Any]) -> dict[str, Any]:
    input_data = {entry["key"]: entry["value"] for entry in case["inputs"]}
    if profile == "java_cpu":
        return _run_java_case(case)

    ir = _case_ir(case["op"], case["params"], case["shape_out"], case["inputs"])
    return execute(
        {
            "ir_dag": ir,
            "input_data": input_data,
            "driver_id": profile,
            "mode": "forward",
            "replay_token": "milestone-9-operator-expansion-v2",
            "tmmu_context": {"arena_config": {"default": {"capacity_bytes": 1_000_000, "alignment_bytes": 64}}},
        }
    )


def _ensure_java_compiled() -> None:
    if JAVA_CLASS_FILE.exists() and JAVA_CLASS_FILE.stat().st_mtime >= JAVA_SRC.stat().st_mtime:
        return
    subprocess.run(["javac", str(JAVA_SRC)], check=True, cwd=str(ROOT))


def _run_java_case(case: dict[str, Any]) -> dict[str, Any]:
    _ensure_java_compiled()
    op = case["op"]
    args: list[str] = []

    if op == "MatMul":
        a = case["inputs"][0]["value"]
        b = case["inputs"][1]["value"]
        args = ["matmul", str(len(a)), str(len(a[0])), _csv(_flatten_2d(a)), str(len(b)), str(len(b[0])), _csv(_flatten_2d(b))]
    elif op == "ReduceSum":
        args = ["reducesum", _csv(case["inputs"][0]["value"])]
    elif op == "Reshape":
        shape = case["params"]["shape"]
        args = ["reshape", str(shape[0]), str(shape[1]), _csv(case["inputs"][0]["value"])]
    elif op == "Transpose":
        m = case["inputs"][0]["value"]
        args = ["transpose", str(len(m)), str(len(m[0])), _csv(_flatten_2d(m))]
    elif op == "Softmax":
        args = ["softmax", _csv(case["inputs"][0]["value"])]
    elif op == "LayerNorm":
        args = [
            "layernorm",
            _csv(case["inputs"][0]["value"]),
            _csv(case["params"]["gamma"]),
            _csv(case["params"]["beta"]),
            str(case["params"]["eps"]),
        ]
    elif op == "MSELoss":
        args = ["mseloss", _csv(case["inputs"][0]["value"]), _csv(case["inputs"][1]["value"])]
    else:
        return {"error": {"code_id": "JAVA_UNSUPPORTED_OP", "message": op}}

    proc = subprocess.run(
        ["java", "-cp", str(JAVA_DIR), JAVA_CLASS, *args],
        capture_output=True,
        text=True,
        check=False,
        cwd=str(ROOT),
    )
    if proc.returncode != 0:
        return {"error": {"code_id": "JAVA_RUNTIME_ERROR", "message": proc.stderr.strip() or "java failed"}}

    try:
        payload = json.loads(proc.stdout.strip())
        return {
            "outputs": payload.get("outputs"),
            "execution_fp": hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest(),
        }
    except Exception as exc:
        return {"error": {"code_id": "JAVA_OUTPUT_PARSE_ERROR", "message": str(exc)}}


def _runtime_meta() -> dict[str, Any]:
    meta: dict[str, Any] = {
        "platform": platform.platform(),
        "kernel": platform.release(),
        "python": sys.version.split()[0],
        "timestamp_utc": datetime.now(UTC).isoformat(),
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

    java_proc = subprocess.run(["java", "-version"], capture_output=True, text=True, cwd=str(ROOT))
    javac_proc = subprocess.run(["javac", "-version"], capture_output=True, text=True, cwd=str(ROOT))
    meta["java"] = {
        "java_version": (java_proc.stderr or java_proc.stdout).strip(),
        "javac_version": (javac_proc.stderr or javac_proc.stdout).strip(),
    }
    return meta


def _compare_results(a: dict[str, Any], b: dict[str, Any], abs_tol: float, rel_tol: float) -> tuple[str, str]:
    if "error" in a or "error" in b:
        return "BLOCKED", "One side returned runtime error."
    ao = a.get("outputs")
    bo = b.get("outputs")
    if ao == bo:
        if a.get("execution_fp") == b.get("execution_fp"):
            return "E0", "Exact output and execution fingerprint match."
        return "E1", "Exact output match; execution fingerprint differs by runtime."
    if _allclose(ao, bo, abs_tol, rel_tol):
        return "E1", "Outputs within tolerance."
    return "E2", "Outputs diverge beyond tolerance."


def main() -> int:
    parser = argparse.ArgumentParser(description="Milestone 9 operator expansion reproducibility matrix.")
    parser.add_argument("--abs-tol", type=float, default=1e-6)
    parser.add_argument("--rel-tol", type=float, default=1e-6)
    parser.add_argument(
        "--output-dir",
        default=str(ROOT / "evidence" / "repro" / "milestone-9-operator-expansion-v2"),
        help="Directory to write report artifacts.",
    )
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    case_reports: list[dict[str, Any]] = []
    for case in CASES:
        profile_results: dict[str, Any] = {}
        for profile in PROFILES:
            profile_results[profile] = _run_profile(profile, case)
        case_reports.append(
            {
                "case_id": case["case_id"],
                "family": case["family"],
                "operator": case["op"],
                "profile_results": profile_results,
            }
        )

    pair_matrix: list[dict[str, Any]] = []
    pair_statuses: list[str] = []
    for a, b in itertools.combinations(PROFILES, 2):
        case_verdicts: list[dict[str, Any]] = []
        has_fail = False
        has_blocked = False
        classifications: list[str] = []

        for case_report in case_reports:
            a_res = case_report["profile_results"][a]
            b_res = case_report["profile_results"][b]
            cls, reason = _compare_results(a_res, b_res, args.abs_tol, args.rel_tol)
            status = "PASS"
            if cls == "E2":
                status = "FAIL"
                has_fail = True
            elif cls == "BLOCKED":
                status = "BLOCKED"
                has_blocked = True
            classifications.append(cls if cls != "BLOCKED" else "E2")
            case_verdicts.append(
                {
                    "case_id": case_report["case_id"],
                    "status": status,
                    "classification": cls,
                    "reason": reason,
                }
            )

        if has_fail:
            pair_status = "FAIL"
            pair_class = "E2"
            pair_reason = "At least one operator case diverged beyond tolerance."
        elif has_blocked:
            pair_status = "BLOCKED"
            pair_class = "E2"
            pair_reason = "At least one operator case blocked by runtime error."
        else:
            pair_status = "PASS"
            pair_class = "E0" if all(c == "E0" for c in classifications) else "E1"
            pair_reason = "All operator cases pass."

        pair_statuses.append(pair_status)
        pair_matrix.append(
            {
                "pair": f"{a}__vs__{b}",
                "status": pair_status,
                "classification": pair_class,
                "reason": pair_reason,
                "cases": case_verdicts,
            }
        )

    if any(s == "FAIL" for s in pair_statuses):
        overall_status = "FAIL"
        overall_class = "E2"
        overall_reason = "At least one required profile pair failed."
    elif any(s == "BLOCKED" for s in pair_statuses):
        overall_status = "BLOCKED"
        overall_class = "E2"
        overall_reason = "At least one required profile pair blocked."
    else:
        overall_status = "PASS"
        overall_class = "E0" if all(p["classification"] == "E0" for p in pair_matrix) else "E1"
        overall_reason = "All required operator expansion pairs pass."

    report = {
        "milestone": 9,
        "profile": "operator_expansion_v2_cross_stack",
        "status": overall_status,
        "classification": overall_class,
        "reason": overall_reason,
        "operators": [c["op"] for c in CASES],
        "cases": case_reports,
        "pairs": pair_matrix,
        "meta": {"abs_tol": args.abs_tol, "rel_tol": args.rel_tol, **_runtime_meta()},
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    repro = {
        "milestone": 9,
        "profile": "operator_expansion_v2_cross_stack",
        "classification": overall_class,
        "status": overall_status,
        "reason": overall_reason,
        "abs_tol": args.abs_tol,
        "rel_tol": args.rel_tol,
        "excluded_operators": [],
    }
    (out_dir / "repro-classification.json").write_text(json.dumps(repro, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "pair-matrix.json").write_text(json.dumps({"pairs": pair_matrix}, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    family_counts: dict[str, int] = {}
    for case in CASES:
        family_counts[case["family"]] = family_counts.get(case["family"], 0) + 1
    coverage = {
        "milestone": 9,
        "operator_case_count": len(CASES),
        "operators": sorted({case["op"] for case in CASES}),
        "families": family_counts,
        "profiles": PROFILES,
        "mandatory_profiles": PROFILES,
        "status": overall_status,
    }
    (out_dir / "coverage-summary.json").write_text(json.dumps(coverage, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "waivers.json").write_text(json.dumps({"waivers": []}, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    env_matrix = report["meta"]
    (out_dir / "env-matrix.json").write_text(json.dumps(env_matrix, indent=2, sort_keys=True) + "\n", encoding="utf-8")

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
        json.dumps(conformance_hashes, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    summary = [
        "# Milestone 9: Operator Expansion v2 (Cross-Stack)",
        "",
        f"Status: {overall_status}",
        f"Classification: {overall_class}",
        f"Reason: {overall_reason}",
        "",
        "## Covered Operator Families",
        "- normalization",
        "- reductions",
        "- matmul_variants",
        "- reshape_transpose",
        "- softmax_loss",
        "",
        "## Profiles",
        "- pytorch_cpu",
        "- pytorch_gpu",
        "- keras_cpu",
        "- keras_gpu",
        "- java_cpu",
        "",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary), encoding="utf-8")
    (out_dir / "known-limitations.md").write_text(
        "# Known Limitations (Milestone 9)\n\n"
        "- Java bridge scope currently covers CPU only.\n"
        "- Operator vectors are deterministic micro-vectors; broader model-level coverage is Milestone 10.\n",
        encoding="utf-8",
    )

    milestone_manifest = {
        "milestone": 9,
        "slug": "operator-expansion-v2",
        "owner": "Astrocytech/Glyphser",
        "target_date": "2026-03-15",
        "dependencies": [8],
        "profiles": PROFILES,
        "result": overall_status,
        "classification": overall_class,
        "evidence_dir": "evidence/repro/milestone-9-operator-expansion-v2/",
    }
    (out_dir / "milestone.json").write_text(json.dumps(milestone_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({"status": overall_status, "classification": overall_class, "reason": overall_reason}, indent=2, sort_keys=True))
    return 0 if overall_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
