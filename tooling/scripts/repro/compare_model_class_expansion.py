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

from runtime.glyphser.model.model_ir_executor import execute

ROOT = Path(__file__).resolve().parents[3]


PROFILES = ["pytorch_cpu", "pytorch_gpu", "keras_cpu", "keras_gpu", "java_cpu"]
JAVA_SRC = ROOT / "tooling" / "scripts" / "repro" / "java_bridge" / "ModelClassExpansionJavaRunner.java"
JAVA_DIR = JAVA_SRC.parent
JAVA_CLASS = "ModelClassExpansionJavaRunner"
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


def _model_ir_mlp() -> dict[str, Any]:
    return {
        "ir_schema_hash": "sha256:milestone10-model-class-expansion",
        "nodes": [
            {
                "node_id": "x",
                "instr": "Input",
                "inputs": [],
                "shape_out": [4],
                "dtype": "float64",
            },
            {
                "node_id": "d1",
                "instr": "Dense",
                "inputs": [{"node_id": "x", "output_idx": 0}],
                "shape_out": [4],
                "dtype": "float64",
                "params": {
                    "weights": [
                        [0.2, -0.1, 0.4, 0.3],
                        [-0.3, 0.8, -0.2, 0.1],
                        [0.5, 0.2, -0.5, 0.7],
                        [0.6, -0.4, 0.1, 0.2],
                    ],
                    "bias": [0.1, -0.2, 0.05, 0.0],
                },
            },
            {
                "node_id": "r1",
                "instr": "Relu",
                "inputs": [{"node_id": "d1", "output_idx": 0}],
                "shape_out": [4],
                "dtype": "float64",
            },
            {
                "node_id": "d2",
                "instr": "Dense",
                "inputs": [{"node_id": "r1", "output_idx": 0}],
                "shape_out": [3],
                "dtype": "float64",
                "params": {
                    "weights": [
                        [0.7, -0.1, 0.2, 0.3],
                        [-0.2, 0.5, 0.4, -0.6],
                        [0.1, 0.2, -0.3, 0.9],
                    ],
                    "bias": [0.01, -0.03, 0.02],
                },
            },
            {
                "node_id": "s2",
                "instr": "Sigmoid",
                "inputs": [{"node_id": "d2", "output_idx": 0}],
                "shape_out": [3],
                "dtype": "float64",
            },
            {
                "node_id": "out",
                "instr": "Output",
                "inputs": [{"node_id": "s2", "output_idx": 0}],
                "shape_out": [3],
                "dtype": "float64",
            },
        ],
        "outputs": [{"node_id": "out", "output_idx": 0}],
    }


def _model_ir_cnn() -> dict[str, Any]:
    return {
        "ir_schema_hash": "sha256:milestone10-model-class-expansion",
        "nodes": [
            {
                "node_id": "x",
                "instr": "Input",
                "inputs": [],
                "shape_out": [6],
                "dtype": "float64",
            },
            {
                "node_id": "conv",
                "instr": "Conv1D",
                "inputs": [{"node_id": "x", "output_idx": 0}],
                "shape_out": [4],
                "dtype": "float64",
                "params": {"kernel": [0.25, -0.5, 0.75], "bias": 0.1},
            },
            {
                "node_id": "relu",
                "instr": "Relu",
                "inputs": [{"node_id": "conv", "output_idx": 0}],
                "shape_out": [4],
                "dtype": "float64",
            },
            {
                "node_id": "dense",
                "instr": "Dense",
                "inputs": [{"node_id": "relu", "output_idx": 0}],
                "shape_out": [2],
                "dtype": "float64",
                "params": {
                    "weights": [[0.6, -0.2, 0.1, 0.5], [-0.3, 0.7, 0.2, -0.4]],
                    "bias": [0.05, -0.08],
                },
            },
            {
                "node_id": "out",
                "instr": "Output",
                "inputs": [{"node_id": "dense", "output_idx": 0}],
                "shape_out": [2],
                "dtype": "float64",
            },
        ],
        "outputs": [{"node_id": "out", "output_idx": 0}],
    }


def _model_ir_attention_lite() -> dict[str, Any]:
    return {
        "ir_schema_hash": "sha256:milestone10-model-class-expansion",
        "nodes": [
            {
                "node_id": "x",
                "instr": "Input",
                "inputs": [],
                "shape_out": [4],
                "dtype": "float64",
            },
            {
                "node_id": "r",
                "instr": "Reshape",
                "inputs": [{"node_id": "x", "output_idx": 0}],
                "shape_out": [2, 2],
                "dtype": "float64",
                "params": {"shape": [2, 2]},
            },
            {
                "node_id": "rt",
                "instr": "Transpose",
                "inputs": [{"node_id": "r", "output_idx": 0}],
                "shape_out": [2, 2],
                "dtype": "float64",
                "params": {"perm": [1, 0]},
            },
            {
                "node_id": "scores",
                "instr": "MatMul",
                "inputs": [
                    {"node_id": "r", "output_idx": 0},
                    {"node_id": "rt", "output_idx": 0},
                ],
                "shape_out": [2, 2],
                "dtype": "float64",
                "params": {},
            },
            {
                "node_id": "attn",
                "instr": "Softmax",
                "inputs": [{"node_id": "scores", "output_idx": 0}],
                "shape_out": [2, 2],
                "dtype": "float64",
                "params": {"axis": -1},
            },
            {
                "node_id": "ctx",
                "instr": "MatMul",
                "inputs": [
                    {"node_id": "attn", "output_idx": 0},
                    {"node_id": "r", "output_idx": 0},
                ],
                "shape_out": [2, 2],
                "dtype": "float64",
                "params": {},
            },
            {
                "node_id": "sum",
                "instr": "ReduceSum",
                "inputs": [{"node_id": "ctx", "output_idx": 0}],
                "shape_out": [1],
                "dtype": "float64",
            },
            {
                "node_id": "out",
                "instr": "Output",
                "inputs": [{"node_id": "sum", "output_idx": 0}],
                "shape_out": [1],
                "dtype": "float64",
            },
        ],
        "outputs": [{"node_id": "out", "output_idx": 0}],
    }


MODELS: list[dict[str, Any]] = [
    {
        "model_id": "mlp_deep",
        "class": "mlp",
        "input": [0.3, -0.7, 1.1, 0.2],
        "ir": _model_ir_mlp,
    },
    {
        "model_id": "cnn_tiny",
        "class": "cnn",
        "input": [0.2, -0.1, 0.5, 1.0, -0.4, 0.7],
        "ir": _model_ir_cnn,
    },
    {
        "model_id": "attention_lite",
        "class": "sequence_attention_lite",
        "input": [0.1, 0.4, -0.6, 1.2],
        "ir": _model_ir_attention_lite,
    },
]


def _ensure_java_compiled() -> None:
    if JAVA_CLASS_FILE.exists() and JAVA_CLASS_FILE.stat().st_mtime >= JAVA_SRC.stat().st_mtime:
        return
    subprocess.run(["javac", str(JAVA_SRC)], check=True, cwd=str(ROOT))


def _run_java_model(model_id: str, model_input: list[float]) -> dict[str, Any]:
    _ensure_java_compiled()
    proc = subprocess.run(
        ["java", "-cp", str(JAVA_DIR), JAVA_CLASS, model_id, _csv(model_input)],
        check=False,
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    if proc.returncode != 0:
        return {
            "error": {
                "code_id": "JAVA_RUNTIME_ERROR",
                "message": proc.stderr.strip() or "java runner failed",
            }
        }
    try:
        payload = json.loads(proc.stdout.strip())
    except Exception as exc:
        return {"error": {"code_id": "JAVA_OUTPUT_PARSE_ERROR", "message": str(exc)}}
    return {
        "outputs": payload.get("outputs"),
        "execution_fp": hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest(),
    }


def _run_profile(profile: str, model: dict[str, Any]) -> dict[str, Any]:
    if profile == "java_cpu":
        return _run_java_model(model["model_id"], model["input"])
    return execute(
        {
            "ir_dag": model["ir"](),
            "input_data": {"x": model["input"]},
            "driver_id": profile,
            "mode": "forward",
            "replay_token": "milestone-10-model-class-expansion",
            "tmmu_context": {"arena_config": {"default": {"capacity_bytes": 1_000_000, "alignment_bytes": 64}}},
        }
    )


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
    except Exception as exc:
        meta["torch"] = {"present": False, "error": str(exc)}

    try:
        import tensorflow as tf

        gpus = tf.config.list_physical_devices("GPU")
        meta["tensorflow"] = {
            "version": tf.__version__,
            "gpu_visible": bool(gpus),
            "gpu_devices": [str(g) for g in gpus],
        }
    except Exception as exc:
        meta["tensorflow"] = {"present": False, "error": str(exc)}

    java_proc = subprocess.run(["java", "-version"], capture_output=True, text=True, cwd=str(ROOT))
    javac_proc = subprocess.run(["javac", "-version"], capture_output=True, text=True, cwd=str(ROOT))
    meta["java"] = {
        "java_version": (java_proc.stderr or java_proc.stdout).strip(),
        "javac_version": (javac_proc.stderr or javac_proc.stdout).strip(),
    }
    return meta


def _compare(a: dict[str, Any], b: dict[str, Any], abs_tol: float, rel_tol: float) -> tuple[str, str]:
    if "error" in a or "error" in b:
        return "BLOCKED", "One side returned runtime error."
    ao, bo = a.get("outputs"), b.get("outputs")
    if ao == bo:
        if a.get("execution_fp") == b.get("execution_fp"):
            return "E0", "Exact output and execution fingerprint match."
        return "E1", "Exact output match; execution fingerprint differs by runtime."
    if _allclose(ao, bo, abs_tol, rel_tol):
        return "E1", "Outputs within tolerance."
    return "E2", "Outputs diverge beyond tolerance."


def main() -> int:
    parser = argparse.ArgumentParser(description="Milestone 10 model class expansion reproducibility matrix.")
    parser.add_argument("--abs-tol", type=float, default=1e-6)
    parser.add_argument("--rel-tol", type=float, default=1e-6)
    parser.add_argument(
        "--output-dir",
        default=str(ROOT / "evidence" / "repro" / "milestone-10-model-class-expansion"),
        help="Directory to write report artifacts.",
    )
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    model_reports: list[dict[str, Any]] = []
    for model in MODELS:
        per_profile: dict[str, Any] = {}
        for profile in PROFILES:
            per_profile[profile] = _run_profile(profile, model)
        model_reports.append(
            {
                "model_id": model["model_id"],
                "model_class": model["class"],
                "profile_results": per_profile,
            }
        )

    pair_matrix: list[dict[str, Any]] = []
    pair_statuses: list[str] = []
    per_model_classification: dict[str, str] = {}

    for a, b in itertools.combinations(PROFILES, 2):
        model_verdicts: list[dict[str, Any]] = []
        has_blocked = False
        has_fail = False
        classes: list[str] = []

        for mr in model_reports:
            cls, reason = _compare(
                mr["profile_results"][a],
                mr["profile_results"][b],
                args.abs_tol,
                args.rel_tol,
            )
            status = "PASS"
            if cls == "BLOCKED":
                status = "BLOCKED"
                has_blocked = True
            elif cls == "E2":
                status = "FAIL"
                has_fail = True
            classes.append("E2" if cls == "BLOCKED" else cls)
            model_verdicts.append(
                {
                    "model_id": mr["model_id"],
                    "model_class": mr["model_class"],
                    "status": status,
                    "classification": cls,
                    "reason": reason,
                }
            )

        if has_fail:
            p_status, p_class, p_reason = (
                "FAIL",
                "E2",
                "At least one model failed tolerance.",
            )
        elif has_blocked:
            p_status, p_class, p_reason = (
                "BLOCKED",
                "E2",
                "At least one model is blocked by runtime error.",
            )
        else:
            p_status = "PASS"
            p_class = "E0" if all(c == "E0" for c in classes) else "E1"
            p_reason = "All model classes pass."

        pair_statuses.append(p_status)
        pair_matrix.append(
            {
                "pair": f"{a}__vs__{b}",
                "status": p_status,
                "classification": p_class,
                "reason": p_reason,
                "models": model_verdicts,
            }
        )

    for mr in model_reports:
        classes: list[str] = []
        blocked = False
        failed = False
        for a, b in itertools.combinations(PROFILES, 2):
            cls, _ = _compare(
                mr["profile_results"][a],
                mr["profile_results"][b],
                args.abs_tol,
                args.rel_tol,
            )
            if cls == "BLOCKED":
                blocked = True
                classes.append("E2")
            elif cls == "E2":
                failed = True
                classes.append("E2")
            else:
                classes.append(cls)
        if failed:
            per_model_classification[mr["model_id"]] = "E2"
        elif blocked:
            per_model_classification[mr["model_id"]] = "E2"
        elif all(c == "E0" for c in classes):
            per_model_classification[mr["model_id"]] = "E0"
        else:
            per_model_classification[mr["model_id"]] = "E1"

    if any(s == "FAIL" for s in pair_statuses):
        overall_status, overall_class, overall_reason = (
            "FAIL",
            "E2",
            "At least one required pair failed.",
        )
    elif any(s == "BLOCKED" for s in pair_statuses):
        overall_status, overall_class, overall_reason = (
            "BLOCKED",
            "E2",
            "At least one required pair blocked.",
        )
    else:
        overall_status = "PASS"
        overall_class = "E0" if all(p["classification"] == "E0" for p in pair_matrix) else "E1"
        overall_reason = "All model class pairs pass."

    report = {
        "milestone": 10,
        "profile": "model_class_expansion_cross_stack",
        "status": overall_status,
        "classification": overall_class,
        "reason": overall_reason,
        "models": model_reports,
        "model_classifications": per_model_classification,
        "pairs": pair_matrix,
        "meta": {"abs_tol": args.abs_tol, "rel_tol": args.rel_tol, **_runtime_meta()},
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    repro = {
        "milestone": 10,
        "profile": "model_class_expansion_cross_stack",
        "classification": overall_class,
        "status": overall_status,
        "reason": overall_reason,
        "abs_tol": args.abs_tol,
        "rel_tol": args.rel_tol,
        "excluded_operators": [],
    }
    (out_dir / "repro-classification.json").write_text(
        json.dumps(repro, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (out_dir / "pair-matrix.json").write_text(
        json.dumps({"pairs": pair_matrix}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    coverage = {
        "milestone": 10,
        "model_count": len(MODELS),
        "model_ids": [m["model_id"] for m in MODELS],
        "model_classes": sorted({m["class"] for m in MODELS}),
        "profiles": PROFILES,
        "mandatory_profiles": PROFILES,
        "status": overall_status,
    }
    (out_dir / "coverage-summary.json").write_text(
        json.dumps(coverage, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (out_dir / "waivers.json").write_text(
        json.dumps({"waivers": []}, indent=2, sort_keys=True) + "\n", encoding="utf-8"
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
        "# Milestone 10: Model Class Expansion",
        "",
        f"Status: {overall_status}",
        f"Classification: {overall_class}",
        f"Reason: {overall_reason}",
        "",
        "## Model Classes",
        "- mlp (mlp_deep)",
        "- cnn (cnn_tiny)",
        "- sequence/attention-lite (attention_lite)",
        "",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines), encoding="utf-8")
    (out_dir / "known-limitations.md").write_text(
        "# Known Limitations (Milestone 10)\n\n"
        "- CNN profile uses deterministic 1D valid convolution primitive (`Conv1D`) for compact parity testing.\n",
        encoding="utf-8",
    )

    milestone_manifest = {
        "milestone": 10,
        "slug": "model-class-expansion",
        "owner": "Astrocytech/Glyphser",
        "target_date": "2026-03-29",
        "dependencies": [9],
        "profiles": PROFILES,
        "result": overall_status,
        "classification": overall_class,
        "evidence_dir": "evidence/repro/milestone-10-model-class-expansion/",
    }
    (out_dir / "milestone.json").write_text(
        json.dumps(milestone_manifest, indent=2, sort_keys=True) + "\n",
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
