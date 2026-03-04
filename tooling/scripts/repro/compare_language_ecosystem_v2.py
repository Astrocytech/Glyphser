#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shlex
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from runtime.glyphser.model.model_ir_executor import execute
from tooling.lib.path_config import fixtures_root

ROOT = Path(__file__).resolve().parents[3]


WAIVER_ADR_M12 = "evidence/repro/decisions/ADR-2026-03-01-m12-resource-gap-temporary-waiver.md"
WAIVER_ADR_M18 = "evidence/repro/decisions/ADR-2026-03-01-m18-device-resource-gap-temporary-waiver.md"
WAIVER_ADR_M19 = "evidence/repro/decisions/ADR-2026-03-01-m19-proceed-under-m18-waiver.md"
WAIVER_ADR_M20 = "evidence/repro/decisions/ADR-2026-03-01-m20-proceed-under-m19-pause.md"

JAVA_BRIDGE = ROOT / "tooling" / "scripts" / "repro" / "java_bridge"
RUST_BRIDGE = ROOT / "tooling" / "scripts" / "repro" / "rust_bridge"
GO_BRIDGE = ROOT / "tooling" / "scripts" / "repro" / "go_bridge"
CPP_BRIDGE = ROOT / "tooling" / "scripts" / "repro" / "cpp_bridge"
CSHARP_BRIDGE = ROOT / "tooling" / "scripts" / "repro" / "csharp_bridge"


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run(cmd: list[str]) -> tuple[int, str, str]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except FileNotFoundError as exc:
        return 127, "", str(exc)


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


def _exec_template(template: str, inputs: list[float], weights: list[float], bias: float) -> dict[str, Any]:
    cmd = (
        template.replace("{input_csv}", ",".join(str(x) for x in inputs))
        .replace("{weights_csv}", ",".join(str(x) for x in weights))
        .replace("{bias}", str(bias))
    )
    try:
        argv = shlex.split(cmd)
    except Exception as exc:
        return {"error": {"code_id": "BAD_COMMAND", "message": str(exc)}}
    code, out, err = _run(argv)
    if code != 0:
        return {
            "error": {
                "code_id": "RUNTIME_EXEC_ERROR",
                "message": err or out or f"code={code}",
            }
        }
    try:
        payload = json.loads(out)
    except Exception as exc:
        return {"error": {"code_id": "OUTPUT_PARSE_ERROR", "message": str(exc)}}
    return {
        "outputs": payload.get("outputs"),
        "execution_fp": hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest(),
        "runtime": payload.get("runtime", ""),
    }


def _compile_if_needed(path_src: Path, path_bin: Path, cmd: list[str]) -> dict[str, Any] | None:
    if path_bin.exists() and path_bin.stat().st_mtime >= path_src.stat().st_mtime:
        return None
    code, out, err = _run(cmd)
    if code != 0:
        return {
            "error": {
                "code_id": "BOOTSTRAP_ERROR",
                "message": err or out or f"compile failed ({code})",
            }
        }
    return None


def _runtime_meta() -> dict[str, Any]:
    meta: dict[str, Any] = {
        "platform": platform.platform(),
        "kernel": platform.release(),
        "python": platform.python_version(),
        "timestamp_utc": datetime.now(UTC).isoformat(),
    }
    for tool in ("go", "g++", "csc", "mcs", "java", "javac", "rustc"):
        code, out, err = _run(
            [tool, "--version"]
            if tool not in {"java", "javac", "g++"}
            else [tool, "-version"]
            if tool in {"java", "javac"}
            else [tool, "--version"]
        )
        meta[tool] = {"ok": code == 0, "version": out or err}
    return meta


def _python_run(driver_id: str, model_ir: dict[str, Any], inputs: list[float]) -> dict[str, Any]:
    return execute(
        {
            "ir_dag": model_ir,
            "input_data": {"input": inputs},
            "driver_id": driver_id,
            "mode": "forward",
            "replay_token": "milestone-20-language-ecosystem-v2",
            "tmmu_context": {"arena_config": {"default": {"capacity_bytes": 1_000_000, "alignment_bytes": 64}}},
        }
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Milestone 20 language ecosystem expansion v2.")
    parser.add_argument("--abs-tol", type=float, default=1e-6)
    parser.add_argument("--rel-tol", type=float, default=1e-6)
    parser.add_argument(
        "--output-dir",
        default=str(ROOT / "evidence" / "repro" / "milestone-20-language-ecosystem-v2"),
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

    results: dict[str, dict[str, Any]] = {}
    results["python_pytorch_cpu"] = _python_run("pytorch_cpu", model_ir, inputs)
    results["python_keras_cpu"] = _python_run("keras_cpu", model_ir, inputs)

    # Java ONNX lane
    onnx_src = JAVA_BRIDGE / "OnnxRuntimeLaneRunner.java"
    onnx_cls = JAVA_BRIDGE / "OnnxRuntimeLaneRunner.class"
    boot = _compile_if_needed(onnx_src, onnx_cls, ["javac", str(onnx_src)])
    onnx_cp = os.pathsep.join([str(JAVA_BRIDGE), os.environ.get("GLYPHSER_ONNX_CLASSPATH", "")]).strip(os.pathsep)
    if boot:
        results["java_onnxruntime_cpu"] = boot
    else:
        results["java_onnxruntime_cpu"] = _exec_template(
            f"java -cp {shlex.quote(onnx_cp)} OnnxRuntimeLaneRunner {{input_csv}} {{weights_csv}} {{bias}}",
            inputs,
            weights,
            bias,
        )

    # Rust lane
    rust_src = RUST_BRIDGE / "RustLaneRunner.rs"
    rust_bin = RUST_BRIDGE / ("RustLaneRunner.exe" if os.name == "nt" else "RustLaneRunner")
    boot = _compile_if_needed(rust_src, rust_bin, ["rustc", str(rust_src), "-O", "-o", str(rust_bin)])
    if boot:
        results["rust_cpu"] = boot
    else:
        results["rust_cpu"] = _exec_template(
            f"{shlex.quote(str(rust_bin))} {{input_csv}} {{weights_csv}} {{bias}}",
            inputs,
            weights,
            bias,
        )

    # Go lane
    go_src = GO_BRIDGE / "GoLaneRunner.go"
    go_bin = GO_BRIDGE / ("GoLaneRunner.exe" if os.name == "nt" else "GoLaneRunner")
    boot = _compile_if_needed(go_src, go_bin, ["go", "build", "-o", str(go_bin), str(go_src)])
    if boot:
        results["go_cpu"] = boot
    else:
        results["go_cpu"] = _exec_template(
            f"{shlex.quote(str(go_bin))} {{input_csv}} {{weights_csv}} {{bias}}",
            inputs,
            weights,
            bias,
        )

    # C++ lane
    cpp_src = CPP_BRIDGE / "CppLaneRunner.cpp"
    cpp_bin = CPP_BRIDGE / ("CppLaneRunner.exe" if os.name == "nt" else "CppLaneRunner")
    boot = _compile_if_needed(cpp_src, cpp_bin, ["g++", "-O2", "-std=c++17", str(cpp_src), "-o", str(cpp_bin)])
    if boot:
        results["cpp_cpu"] = boot
    else:
        results["cpp_cpu"] = _exec_template(
            f"{shlex.quote(str(cpp_bin))} {{input_csv}} {{weights_csv}} {{bias}}",
            inputs,
            weights,
            bias,
        )

    # C# lane
    cs_src = CSHARP_BRIDGE / "CSharpLaneRunner.cs"
    cs_bin = CSHARP_BRIDGE / ("CSharpLaneRunner.exe")
    csharp_boot = None
    for compiler in (
        ["csc", "/nologo", f"/out:{cs_bin}", str(cs_src)],
        ["mcs", "-out:" + str(cs_bin), str(cs_src)],
    ):
        csharp_boot = _compile_if_needed(cs_src, cs_bin, compiler)
        if csharp_boot is None:
            break
    if csharp_boot:
        results["csharp_cpu"] = csharp_boot
    else:
        csharp_runner = f"mono {shlex.quote(str(cs_bin))}" if os.name != "nt" else shlex.quote(str(cs_bin))
        results["csharp_cpu"] = _exec_template(
            csharp_runner + " {input_csv} {weights_csv} {bias}", inputs, weights, bias
        )

    baseline = results["python_pytorch_cpu"]
    pair_rows = []
    language_rows = []
    for lane, out in results.items():
        if lane == "python_pytorch_cpu":
            language_rows.append({"language_lane": lane, "status": "PASS"})
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
            language_rows.append({"language_lane": lane, "status": "BLOCKED"})
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
        language_rows.append({"language_lane": lane, "status": status})

    statuses = [r["status"] for r in pair_rows]
    if any(s == "FAIL" for s in statuses):
        overall_status, overall_class, overall_reason = (
            "FAIL",
            "E2",
            "At least one language lane failed.",
        )
    elif any(s == "BLOCKED" for s in statuses):
        overall_status, overall_class, overall_reason = (
            "BLOCKED",
            "E2",
            "At least one language lane is blocked.",
        )
    else:
        overall_status = "PASS"
        overall_class = "E0" if all(r["classification"] == "E0" for r in pair_rows) else "E1"
        overall_reason = "All language lanes pass."

    report = {
        "milestone": 20,
        "profile": "language_ecosystem_v2",
        "status": overall_status,
        "classification": overall_class,
        "reason": overall_reason,
        "results": results,
        "pairs": pair_rows,
        "language_matrix": language_rows,
        "meta": {"abs_tol": args.abs_tol, "rel_tol": args.rel_tol, **_runtime_meta()},
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "repro-classification.json").write_text(
        json.dumps(
            {
                "milestone": 20,
                "profile": "language_ecosystem_v2",
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
    (out_dir / "language-matrix.json").write_text(
        json.dumps({"language_matrix": language_rows}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "env-matrix.json").write_text(
        json.dumps(report["meta"], indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (out_dir / "coverage-summary.json").write_text(
        json.dumps(
            {"milestone": 20, "lane_count": len(results), "status": overall_status},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (out_dir / "device-matrix.json").write_text(
        json.dumps(
            {"note": "Milestone 20 focuses on language lanes."},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (out_dir / "os-matrix.json").write_text(
        json.dumps({"note": "Milestone 20 assumes current host OS."}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "library-matrix.json").write_text(
        json.dumps(
            {"note": "Milestone 20 focuses on language runtimes."},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (out_dir / "portability-gaps.md").write_text(
        "# Portability Gaps (Milestone 20)\n\n"
        + "\n".join(
            f"- `{lane}` blocked: {res['error']['message']}"
            for lane, res in results.items()
            if isinstance(res, dict) and "error" in res
        )
        + "\n",
        encoding="utf-8",
    )
    waivers = []
    for adr in (WAIVER_ADR_M12, WAIVER_ADR_M18, WAIVER_ADR_M19, WAIVER_ADR_M20):
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
                "# Milestone 20: Language Ecosystem Expansion v2",
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
        "# Known Limitations (Milestone 20)\n\n"
        "- Requires host toolchains for Go/C++/C# lanes.\n"
        "- Java ONNX lane requires GLYPHSER_ONNX_CLASSPATH.\n",
        encoding="utf-8",
    )
    (out_dir / "milestone.json").write_text(
        json.dumps(
            {
                "milestone": 20,
                "slug": "language-ecosystem-v2",
                "owner": "Astrocytech/Glyphser",
                "target_date": "2026-10-22",
                "dependencies": [19],
                "waiver_dependencies": [19],
                "profiles": list(results.keys()),
                "result": overall_status,
                "classification": overall_class,
                "evidence_dir": "evidence/repro/milestone-20-language-ecosystem-v2/",
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
