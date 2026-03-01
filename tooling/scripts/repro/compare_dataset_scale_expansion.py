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

PROFILES = ["pytorch_cpu", "pytorch_gpu", "keras_cpu", "keras_gpu", "java_cpu"]
JAVA_DIR = ROOT / "tooling" / "scripts" / "repro" / "java_bridge"
JAVA_CLASS = "ModelClassExpansionJavaRunner"
JAVA_SRC = JAVA_DIR / f"{JAVA_CLASS}.java"
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


def _lcg(seed: int) -> float:
    value = (seed * 1664525 + 1013904223) & 0xFFFFFFFF
    return (value / 4294967296.0) * 2.0 - 1.0


def _dataset(dim: int, count: int, seed: int) -> list[list[float]]:
    out: list[list[float]] = []
    state = seed
    for _ in range(count):
        row: list[float] = []
        for _ in range(dim):
            state = (state * 1664525 + 1013904223) & 0xFFFFFFFF
            row.append((state / 4294967296.0) * 2.0 - 1.0)
        out.append(row)
    return out


def _model_ir_mlp() -> dict[str, Any]:
    return {
        "ir_schema_hash": "sha256:milestone11-dataset-scale-expansion",
        "nodes": [
            {"node_id": "x", "instr": "Input", "inputs": [], "shape_out": [4], "dtype": "float64"},
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
            {"node_id": "r1", "instr": "Relu", "inputs": [{"node_id": "d1", "output_idx": 0}], "shape_out": [4], "dtype": "float64"},
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
            {"node_id": "s2", "instr": "Sigmoid", "inputs": [{"node_id": "d2", "output_idx": 0}], "shape_out": [3], "dtype": "float64"},
            {"node_id": "out", "instr": "Output", "inputs": [{"node_id": "s2", "output_idx": 0}], "shape_out": [3], "dtype": "float64"},
        ],
        "outputs": [{"node_id": "out", "output_idx": 0}],
    }


def _model_ir_cnn() -> dict[str, Any]:
    return {
        "ir_schema_hash": "sha256:milestone11-dataset-scale-expansion",
        "nodes": [
            {"node_id": "x", "instr": "Input", "inputs": [], "shape_out": [6], "dtype": "float64"},
            {
                "node_id": "conv",
                "instr": "Conv1D",
                "inputs": [{"node_id": "x", "output_idx": 0}],
                "shape_out": [4],
                "dtype": "float64",
                "params": {"kernel": [0.25, -0.5, 0.75], "bias": 0.1},
            },
            {"node_id": "relu", "instr": "Relu", "inputs": [{"node_id": "conv", "output_idx": 0}], "shape_out": [4], "dtype": "float64"},
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
            {"node_id": "out", "instr": "Output", "inputs": [{"node_id": "dense", "output_idx": 0}], "shape_out": [2], "dtype": "float64"},
        ],
        "outputs": [{"node_id": "out", "output_idx": 0}],
    }


def _model_ir_attention_lite() -> dict[str, Any]:
    return {
        "ir_schema_hash": "sha256:milestone11-dataset-scale-expansion",
        "nodes": [
            {"node_id": "x", "instr": "Input", "inputs": [], "shape_out": [4], "dtype": "float64"},
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
                "inputs": [{"node_id": "r", "output_idx": 0}, {"node_id": "rt", "output_idx": 0}],
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
                "inputs": [{"node_id": "attn", "output_idx": 0}, {"node_id": "r", "output_idx": 0}],
                "shape_out": [2, 2],
                "dtype": "float64",
                "params": {},
            },
            {"node_id": "sum", "instr": "ReduceSum", "inputs": [{"node_id": "ctx", "output_idx": 0}], "shape_out": [1], "dtype": "float64"},
            {"node_id": "out", "instr": "Output", "inputs": [{"node_id": "sum", "output_idx": 0}], "shape_out": [1], "dtype": "float64"},
        ],
        "outputs": [{"node_id": "out", "output_idx": 0}],
    }


MODEL_SPECS: list[dict[str, Any]] = [
    {"model_id": "mlp_deep", "model_class": "mlp", "input_dim": 4, "ir": _model_ir_mlp},
    {"model_id": "cnn_tiny", "model_class": "cnn", "input_dim": 6, "ir": _model_ir_cnn},
    {"model_id": "attention_lite", "model_class": "sequence_attention_lite", "input_dim": 4, "ir": _model_ir_attention_lite},
]

DATASET_TIERS = [
    {"tier": "medium", "count": 16, "horizon": 4, "seed": 101},
    {"tier": "large", "count": 48, "horizon": 8, "seed": 313},
]


def _ensure_java_compiled() -> None:
    if JAVA_CLASS_FILE.exists() and JAVA_CLASS_FILE.stat().st_mtime >= JAVA_SRC.stat().st_mtime:
        return
    subprocess.run(["javac", str(JAVA_SRC)], check=True, cwd=str(ROOT))


def _run_java_model(model_id: str, model_input: list[float]) -> dict[str, Any]:
    _ensure_java_compiled()
    proc = subprocess.run(
        ["java", "-cp", str(JAVA_DIR), JAVA_CLASS, model_id, ",".join(str(v) for v in model_input)],
        check=False,
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    if proc.returncode != 0:
        return {"error": {"code_id": "JAVA_RUNTIME_ERROR", "message": proc.stderr.strip() or "java runner failed"}}
    try:
        payload = json.loads(proc.stdout.strip())
    except Exception as exc:
        return {"error": {"code_id": "JAVA_OUTPUT_PARSE_ERROR", "message": str(exc)}}
    return {
        "outputs": payload.get("outputs"),
        "execution_fp": hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest(),
    }


def _run_model_once(profile: str, model: dict[str, Any], input_vec: list[float], replay_token: str) -> dict[str, Any]:
    if profile == "java_cpu":
        return _run_java_model(model["model_id"], input_vec)
    return execute(
        {
            "ir_dag": model["ir"](),
            "input_data": {"x": input_vec},
            "driver_id": profile,
            "mode": "forward",
            "replay_token": replay_token,
            "tmmu_context": {"arena_config": {"default": {"capacity_bytes": 1_000_000, "alignment_bytes": 64}}},
        }
    )


def _run_profile_dataset(profile: str, model: dict[str, Any], samples: list[list[float]], horizon: int) -> dict[str, Any]:
    outputs: list[Any] = []
    fingerprints: list[str] = []

    for idx, sample in enumerate(samples):
        replay_token = f"m11:{model['model_id']}:{idx}"
        first = _run_model_once(profile, model, sample, replay_token)
        if "error" in first:
            return first

        for step in range(1, horizon):
            nxt = _run_model_once(profile, model, sample, replay_token)
            if "error" in nxt:
                return nxt
            # Intra-profile replay stability for same input/token.
            if not _allclose(first.get("outputs"), nxt.get("outputs"), 1e-12, 1e-12):
                return {
                    "error": {
                        "code_id": "REPLAY_DIVERGENCE",
                        "message": f"replay divergence at sample={idx} step={step}",
                    }
                }

        outputs.append(first.get("outputs"))
        fingerprints.append(first.get("execution_fp", ""))

    dataset_fp = hashlib.sha256(json.dumps(outputs, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    return {
        "dataset_outputs": outputs,
        "dataset_fp": dataset_fp,
        "execution_fps": fingerprints,
        "sample_count": len(samples),
        "horizon": horizon,
    }


def _compare_profile_results(a: dict[str, Any], b: dict[str, Any], abs_tol: float, rel_tol: float) -> tuple[str, str, float]:
    if "error" in a or "error" in b:
        return "BLOCKED", "One side returned runtime error.", float("inf")

    ao = a["dataset_outputs"]
    bo = b["dataset_outputs"]

    max_abs = 0.0

    def walk(x: Any, y: Any) -> bool:
        nonlocal max_abs
        if isinstance(x, (int, float)) and isinstance(y, (int, float)):
            diff = abs(float(x) - float(y))
            max_abs = max(max_abs, diff)
            scale = max(abs(float(x)), abs(float(y)), 1.0)
            return diff <= max(abs_tol, rel_tol * scale)
        if isinstance(x, list) and isinstance(y, list) and len(x) == len(y):
            return all(walk(xi, yi) for xi, yi in zip(x, y))
        if isinstance(x, dict) and isinstance(y, dict) and set(x.keys()) == set(y.keys()):
            return all(walk(x[k], y[k]) for k in x)
        return x == y

    same_outputs = ao == bo
    if same_outputs:
        if a.get("dataset_fp") == b.get("dataset_fp"):
            return "E0", "Exact dataset output/fingerprint match.", 0.0
        return "E1", "Exact outputs with runtime-specific fingerprint delta.", 0.0

    if walk(ao, bo):
        return "E1", "Dataset outputs within tolerance.", max_abs

    return "E2", "Dataset outputs diverge beyond tolerance.", max_abs


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


def main() -> int:
    parser = argparse.ArgumentParser(description="Milestone 11 dataset and scale expansion reproducibility checks.")
    parser.add_argument("--abs-tol", type=float, default=1e-6)
    parser.add_argument("--rel-tol", type=float, default=1e-6)
    parser.add_argument(
        "--output-dir",
        default=str(ROOT / "evidence" / "repro" / "milestone-11-dataset-scale-expansion"),
        help="Directory to write report artifacts.",
    )
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    run_matrix: list[dict[str, Any]] = []
    drift_records: list[dict[str, Any]] = []
    pair_rows: list[dict[str, Any]] = []
    pair_statuses: list[str] = []

    for tier in DATASET_TIERS:
        tier_models: list[dict[str, Any]] = []
        for model in MODEL_SPECS:
            samples = _dataset(model["input_dim"], tier["count"], tier["seed"] + len(model["model_id"]))
            per_profile: dict[str, Any] = {}
            for profile in PROFILES:
                per_profile[profile] = _run_profile_dataset(profile, model, samples, tier["horizon"])
            tier_models.append(
                {
                    "tier": tier["tier"],
                    "model_id": model["model_id"],
                    "model_class": model["model_class"],
                    "sample_count": tier["count"],
                    "horizon": tier["horizon"],
                    "profile_results": per_profile,
                }
            )

        run_matrix.extend(tier_models)

        for a, b in itertools.combinations(PROFILES, 2):
            model_verdicts: list[dict[str, Any]] = []
            has_fail = False
            has_blocked = False
            cls_all: list[str] = []
            max_pair_drift = 0.0

            for row in tier_models:
                cls, reason, max_abs = _compare_profile_results(
                    row["profile_results"][a], row["profile_results"][b], args.abs_tol, args.rel_tol
                )
                status = "PASS"
                if cls == "BLOCKED":
                    status = "BLOCKED"
                    has_blocked = True
                elif cls == "E2":
                    status = "FAIL"
                    has_fail = True
                cls_all.append("E2" if cls == "BLOCKED" else cls)
                max_pair_drift = max(max_pair_drift, 0.0 if max_abs == float("inf") else max_abs)
                model_verdicts.append(
                    {
                        "model_id": row["model_id"],
                        "model_class": row["model_class"],
                        "status": status,
                        "classification": cls,
                        "reason": reason,
                        "max_abs_drift": None if max_abs == float("inf") else max_abs,
                    }
                )

            if has_fail:
                p_status, p_class, p_reason = "FAIL", "E2", "At least one model/tier failed tolerance."
            elif has_blocked:
                p_status, p_class, p_reason = "BLOCKED", "E2", "At least one model/tier blocked by runtime error."
            else:
                p_status = "PASS"
                p_class = "E0" if all(c == "E0" for c in cls_all) else "E1"
                p_reason = "All model/tier checks pass."

            pair_statuses.append(p_status)
            pair_rows.append(
                {
                    "tier": tier["tier"],
                    "pair": f"{a}__vs__{b}",
                    "status": p_status,
                    "classification": p_class,
                    "reason": p_reason,
                    "max_abs_drift": max_pair_drift,
                    "models": model_verdicts,
                }
            )
            drift_records.append(
                {
                    "tier": tier["tier"],
                    "pair": f"{a}__vs__{b}",
                    "max_abs_drift": max_pair_drift,
                }
            )

    if any(s == "FAIL" for s in pair_statuses):
        overall_status, overall_class, overall_reason = "FAIL", "E2", "At least one required pair failed."
    elif any(s == "BLOCKED" for s in pair_statuses):
        overall_status, overall_class, overall_reason = "BLOCKED", "E2", "At least one required pair blocked."
    else:
        overall_status = "PASS"
        overall_class = "E0" if all(r["classification"] == "E0" for r in pair_rows) else "E1"
        overall_reason = "All dataset/scale reproducibility checks pass."

    report = {
        "milestone": 11,
        "profile": "dataset_scale_expansion_cross_stack",
        "status": overall_status,
        "classification": overall_class,
        "reason": overall_reason,
        "tiers": DATASET_TIERS,
        "runs": run_matrix,
        "pairs": pair_rows,
        "drift_records": drift_records,
        "meta": {"abs_tol": args.abs_tol, "rel_tol": args.rel_tol, **_runtime_meta()},
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    repro = {
        "milestone": 11,
        "profile": "dataset_scale_expansion_cross_stack",
        "classification": overall_class,
        "status": overall_status,
        "reason": overall_reason,
        "abs_tol": args.abs_tol,
        "rel_tol": args.rel_tol,
        "excluded_operators": [],
    }
    (out_dir / "repro-classification.json").write_text(json.dumps(repro, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "pair-matrix.json").write_text(json.dumps({"pairs": pair_rows}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "drift-envelope.json").write_text(json.dumps({"drift_records": drift_records}, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    coverage = {
        "milestone": 11,
        "status": overall_status,
        "dataset_tiers": [t["tier"] for t in DATASET_TIERS],
        "sample_counts": {t["tier"]: t["count"] for t in DATASET_TIERS},
        "horizons": {t["tier"]: t["horizon"] for t in DATASET_TIERS},
        "model_ids": [m["model_id"] for m in MODEL_SPECS],
        "model_classes": sorted({m["model_class"] for m in MODEL_SPECS}),
        "profiles": PROFILES,
        "mandatory_profiles": PROFILES,
    }
    (out_dir / "coverage-summary.json").write_text(json.dumps(coverage, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "waivers.json").write_text(json.dumps({"waivers": []}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "env-matrix.json").write_text(json.dumps(report["meta"], indent=2, sort_keys=True) + "\n", encoding="utf-8")

    conformance_hashes: dict[str, Any] = {"status": overall_status}
    results_path = ROOT / "evidence" / "conformance" / "results" / "latest.json"
    conformance_path = ROOT / "evidence" / "conformance" / "reports" / "latest.json"
    if results_path.exists():
        conformance_hashes["conformance_results"] = {
            "path": "evidence/conformance/results/latest.json",
            "sha256": _sha256_file(results_path),
        }
    if conformance_path.exists():
        conformance_hashes["conformance_report"] = {
            "path": "evidence/conformance/reports/latest.json",
            "sha256": _sha256_file(conformance_path),
        }
    (out_dir / "conformance-hashes.json").write_text(json.dumps(conformance_hashes, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    summary_lines = [
        "# Milestone 11: Dataset and Scale Expansion",
        "",
        f"Status: {overall_status}",
        f"Classification: {overall_class}",
        f"Reason: {overall_reason}",
        "",
        "## Dataset Tiers",
        "- medium: 16 samples, replay horizon 4",
        "- large: 48 samples, replay horizon 8",
        "",
        "## Model Classes",
        "- mlp",
        "- cnn",
        "- sequence_attention_lite",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
    (out_dir / "known-limitations.md").write_text(
        "# Known Limitations (Milestone 11)\n\n"
        "- Large tier is deterministic functional replay scale test, not full model training-convergence replay.\n",
        encoding="utf-8",
    )

    milestone_manifest = {
        "milestone": 11,
        "slug": "dataset-scale-expansion",
        "owner": "Astrocytech/Glyphser",
        "target_date": "2026-04-19",
        "dependencies": [10],
        "profiles": PROFILES,
        "result": overall_status,
        "classification": overall_class,
        "evidence_dir": "evidence/repro/milestone-11-dataset-scale-expansion/",
    }
    (out_dir / "milestone.json").write_text(json.dumps(milestone_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({"status": overall_status, "classification": overall_class, "reason": overall_reason}, indent=2, sort_keys=True))
    return 0 if overall_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
