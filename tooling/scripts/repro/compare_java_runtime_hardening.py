#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shlex
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from runtime.glyphser.model.model_ir_executor import execute  # noqa: E402
from tooling.lib.path_config import fixtures_root  # noqa: E402

PYTORCH_PROFILES = ["pytorch_cpu", "pytorch_gpu"]
JAVA_RUNTIME_PROFILES = {
    "java_onnxruntime_cpu": "onnxruntime_java",
    "java_djl_cpu": "djl",
}
JAVA_BRIDGE_DIR = ROOT / "tooling" / "scripts" / "repro" / "java_bridge"
ONNX_RUNNER_SRC = JAVA_BRIDGE_DIR / "OnnxRuntimeLaneRunner.java"
DJL_RUNNER_SRC = JAVA_BRIDGE_DIR / "DjlLaneRunner.java"
ONNX_RUNNER_CLASS = "OnnxRuntimeLaneRunner"
DJL_RUNNER_CLASS = "DjlLaneRunner"

WAIVER_ADR = "evidence/repro/decisions/ADR-2026-03-01-m12-resource-gap-temporary-waiver.md"


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_dataset(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


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


def _run(cmd: list[str]) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except FileNotFoundError as exc:
        return 127, "", str(exc)


def _quote_arg(value: str) -> str:
    return shlex.quote(value)


def _classpath_with_local(cp_extra: str) -> str:
    parts = [str(JAVA_BRIDGE_DIR)]
    if cp_extra.strip():
        parts.append(cp_extra.strip())
    return os.pathsep.join(parts)


def _ensure_runner_compiled(src: Path, class_name: str) -> None:
    class_file = src.with_suffix(".class")
    if class_file.exists() and class_file.stat().st_mtime >= src.stat().st_mtime:
        return
    code, out, err = _run(["javac", str(src)])
    if code != 0:
        raise RuntimeError(f"javac failed for {class_name}: {err or out}")


def _default_lane_cmd(runner_class: str, classpath_extra: str) -> str:
    cp = _classpath_with_local(classpath_extra)
    return f"java -cp {_quote_arg(cp)} {runner_class} {{input_csv}} {{weights_csv}} {{bias}}"


def _exec_with_template(template: str, inputs: list[float], weights: list[float], bias: float) -> dict[str, Any]:
    if not template.strip():
        return {
            "error": {
                "code_id": "JAVA_RUNTIME_NOT_CONFIGURED",
                "message": "Missing runtime command template.",
            }
        }

    replacements = {
        "{input_csv}": ",".join(str(x) for x in inputs),
        "{weights_csv}": ",".join(str(x) for x in weights),
        "{bias}": str(bias),
    }
    command = template
    for key, value in replacements.items():
        command = command.replace(key, value)

    try:
        argv = shlex.split(command)
    except ValueError as exc:
        return {"error": {"code_id": "JAVA_RUNTIME_BAD_COMMAND", "message": str(exc)}}

    code, out, err = _run(argv)
    if code != 0:
        return {
            "error": {
                "code_id": "JAVA_RUNTIME_ERROR",
                "message": err or out or f"runtime command failed with code {code}",
            }
        }
    try:
        payload = json.loads(out)
    except json.JSONDecodeError as exc:
        return {
            "error": {
                "code_id": "JAVA_OUTPUT_PARSE_ERROR",
                "message": str(exc),
            }
        }
    return {
        "outputs": payload.get("outputs"),
        "execution_fp": hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest(),
    }


def _run_pytorch(driver_id: str, model_ir: dict[str, Any], inputs: list[float]) -> dict[str, Any]:
    return execute(
        {
            "ir_dag": model_ir,
            "input_data": {"input": inputs},
            "driver_id": driver_id,
            "mode": "forward",
            "replay_token": "milestone-13-java-runtime-hardening",
            "tmmu_context": {"arena_config": {"default": {"capacity_bytes": 1_000_000, "alignment_bytes": 64}}},
        }
    )


def _compare(a: dict[str, Any], b: dict[str, Any], abs_tol: float, rel_tol: float) -> tuple[str, str]:
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


def _runtime_meta(onnx_template: str, djl_template: str) -> dict[str, Any]:
    meta: dict[str, Any] = {
        "platform": platform.platform(),
        "kernel": platform.release(),
        "python": sys.version.split()[0],
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "java_runtime_templates": {
            "onnxruntime_java": onnx_template,
            "djl": djl_template,
        },
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

    java_code, java_out, java_err = _run(["java", "-version"])
    javac_code, javac_out, javac_err = _run(["javac", "-version"])
    meta["java"] = {
        "java_ok": java_code == 0,
        "javac_ok": javac_code == 0,
        "java_version": java_err or java_out,
        "javac_version": javac_err or javac_out,
    }
    return meta


def main() -> int:
    parser = argparse.ArgumentParser(description="Milestone 13 Java runtime hardening matrix.")
    parser.add_argument("--abs-tol", type=float, default=1e-6)
    parser.add_argument("--rel-tol", type=float, default=1e-6)
    parser.add_argument(
        "--onnx-java-cmd",
        default="",
        help=("Command template for ONNX Runtime Java lane. Use placeholders: {input_csv} {weights_csv} {bias}"),
    )
    parser.add_argument(
        "--djl-java-cmd",
        default="",
        help=("Command template for DJL lane. Use placeholders: {input_csv} {weights_csv} {bias}"),
    )
    parser.add_argument(
        "--onnx-classpath",
        default=os.environ.get("GLYPHSER_ONNX_CLASSPATH", ""),
        help="Extra classpath for ONNX Runtime Java jars. Local java_bridge path is added automatically.",
    )
    parser.add_argument(
        "--djl-classpath",
        default=os.environ.get("GLYPHSER_DJL_CLASSPATH", ""),
        help="Extra classpath for DJL jars. Local java_bridge path is added automatically.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(ROOT / "evidence" / "repro" / "milestone-13-java-runtime-hardening"),
    )
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    fixtures = fixtures_root() / "hello-core"
    dataset = _load_dataset(fixtures / "tiny_synth_dataset.jsonl")
    model_ir = json.loads((fixtures / "model_ir.json").read_text(encoding="utf-8"))
    inputs = dataset[0]["x"]

    dense_node = next((n for n in model_ir.get("nodes", []) if n.get("instr") == "Dense"), None)
    if dense_node is None:
        raise RuntimeError("Dense node not found in hello-core model_ir.json")
    params = dense_node.get("params", {})
    weights = params.get("weights", [])
    bias = float(params.get("bias", 0.0))

    _ensure_runner_compiled(ONNX_RUNNER_SRC, ONNX_RUNNER_CLASS)
    _ensure_runner_compiled(DJL_RUNNER_SRC, DJL_RUNNER_CLASS)
    onnx_cmd = args.onnx_java_cmd.strip() or _default_lane_cmd(ONNX_RUNNER_CLASS, args.onnx_classpath)
    djl_cmd = args.djl_java_cmd.strip() or _default_lane_cmd(DJL_RUNNER_CLASS, args.djl_classpath)

    profile_results: dict[str, Any] = {}
    for p in PYTORCH_PROFILES:
        profile_results[p] = _run_pytorch(p, model_ir, inputs)
    profile_results["java_onnxruntime_cpu"] = _exec_with_template(onnx_cmd, inputs, weights, bias)
    profile_results["java_djl_cpu"] = _exec_with_template(djl_cmd, inputs, weights, bias)

    pairs = [
        ("pytorch_cpu", "java_onnxruntime_cpu"),
        ("pytorch_gpu", "java_onnxruntime_cpu"),
        ("pytorch_cpu", "java_djl_cpu"),
        ("pytorch_gpu", "java_djl_cpu"),
        ("java_onnxruntime_cpu", "java_djl_cpu"),
    ]
    pair_matrix: list[dict[str, Any]] = []
    pair_statuses: list[str] = []

    for a, b in pairs:
        cls, reason = _compare(profile_results[a], profile_results[b], args.abs_tol, args.rel_tol)
        status = "PASS"
        if cls == "BLOCKED":
            status = "BLOCKED"
        elif cls == "E2":
            status = "FAIL"
        pair_statuses.append(status)
        pair_matrix.append(
            {
                "pair": f"{a}__vs__{b}",
                "status": status,
                "classification": cls,
                "reason": reason,
                "a_result": profile_results[a],
                "b_result": profile_results[b],
            }
        )

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
            "At least one required pair is blocked.",
        )
    else:
        overall_status = "PASS"
        overall_class = "E0" if all(p["classification"] == "E0" for p in pair_matrix) else "E1"
        overall_reason = "All PyTorch↔Java runtime hardening pairs pass."

    report = {
        "milestone": 13,
        "profile": "java_runtime_hardening",
        "status": overall_status,
        "classification": overall_class,
        "reason": overall_reason,
        "profiles": profile_results,
        "pairs": pair_matrix,
        "meta": {
            "abs_tol": args.abs_tol,
            "rel_tol": args.rel_tol,
            **_runtime_meta(onnx_cmd, djl_cmd),
        },
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    repro = {
        "milestone": 13,
        "profile": "java_runtime_hardening",
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
    (out_dir / "env-matrix.json").write_text(
        json.dumps(report["meta"], indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    coverage = {
        "milestone": 13,
        "profiles": [
            "pytorch_cpu",
            "pytorch_gpu",
            "java_onnxruntime_cpu",
            "java_djl_cpu",
        ],
        "mandatory_profiles": [
            "pytorch_cpu",
            "pytorch_gpu",
            "java_onnxruntime_cpu",
            "java_djl_cpu",
        ],
        "java_runtime_lanes": ["onnxruntime_java", "djl"],
        "status": overall_status,
    }
    (out_dir / "coverage-summary.json").write_text(
        json.dumps(coverage, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

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

    summary = [
        "# Milestone 13: Java Runtime Hardening",
        "",
        f"Status: {overall_status}",
        f"Classification: {overall_class}",
        f"Reason: {overall_reason}",
        "",
        "## Java Runtime Lanes",
        "- onnxruntime_java",
        "- djl",
        "",
        "## Required Inputs",
        "- Option A: provide --onnx-java-cmd and --djl-java-cmd templates.",
        "- Option B: provide --onnx-classpath and --djl-classpath; defaults build commands automatically.",
        "- Placeholder support for explicit templates: {input_csv}, {weights_csv}, {bias}.",
    ]
    (out_dir / "summary.md").write_text("\n".join(summary) + "\n", encoding="utf-8")

    known_limitations = (
        "# Known Limitations (Milestone 13)\n\n"
        "- Java lane commands are user-provided templates. "
        "If either lane is missing, milestone status becomes BLOCKED.\n"
        "- This script validates deterministic bridge outputs at the parity layer; "
        "runtime-specific performance behavior is out of scope.\n"
    )
    (out_dir / "known-limitations.md").write_text(known_limitations, encoding="utf-8")

    milestone_manifest = {
        "milestone": 13,
        "slug": "java-runtime-hardening",
        "owner": "Astrocytech/Glyphser",
        "target_date": "2026-05-31",
        "dependencies": [11],
        "waiver_dependencies": [12],
        "profiles": [
            "pytorch_cpu",
            "pytorch_gpu",
            "java_onnxruntime_cpu",
            "java_djl_cpu",
        ],
        "result": overall_status,
        "classification": overall_class,
        "evidence_dir": "evidence/repro/milestone-13-java-runtime-hardening/",
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
