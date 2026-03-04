#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from runtime.glyphser.serialization.canonical_cbor import (
    encode_canonical,
    encode_canonical_hex,
)
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


def _check_onnx_roundtrip(
    inputs: list[float],
    weights: list[float],
    bias: float,
    abs_tol: float,
    rel_tol: float,
) -> dict[str, Any]:
    try:
        import numpy as np
        import onnx
        import onnxruntime as ort
        from onnx import TensorProto, helper
    except Exception as exc:
        return {
            "check": "onnx_roundtrip",
            "status": "BLOCKED",
            "classification": "E2",
            "reason": str(exc),
        }

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
    model = helper.make_model(graph, producer_name="glyphser-m22")
    onnx.checker.check_model(model)
    x = np.array([inputs], dtype=np.float64)
    expected = [
        [
            float(
                np.dot(
                    np.array(inputs, dtype=np.float64),
                    np.array(weights, dtype=np.float64),
                )
                + bias
            )
        ]
    ]
    with tempfile.TemporaryDirectory(prefix="glyphser-m22-onnx-") as td:
        p = Path(td) / "model.onnx"
        p.write_bytes(model.SerializeToString())
        sess = ort.InferenceSession(str(p), providers=["CPUExecutionProvider"])
        y = sess.run(None, {"X": x})[0]
    observed = [[float(y[0][0])]]
    ok = _allclose(expected, observed, abs_tol, rel_tol)
    return {
        "check": "onnx_roundtrip",
        "status": "PASS" if ok else "FAIL",
        "classification": "E1" if ok else "E2",
        "reason": "ONNX export/import output matches expected tolerance." if ok else "ONNX roundtrip output mismatch.",
        "expected": expected,
        "observed": observed,
    }


def _check_safetensors_roundtrip(
    inputs: list[float],
    weights: list[float],
    bias: float,
    abs_tol: float,
    rel_tol: float,
) -> dict[str, Any]:
    try:
        import numpy as np
        from safetensors.numpy import load_file, save_file
    except Exception as exc:
        return {
            "check": "safetensors_roundtrip",
            "status": "BLOCKED",
            "classification": "E2",
            "reason": str(exc),
        }

    arr_in = np.array(inputs, dtype=np.float64)
    arr_w = np.array(weights, dtype=np.float64)
    arr_b = np.array([bias], dtype=np.float64)
    with tempfile.TemporaryDirectory(prefix="glyphser-m22-st-") as td:
        p = Path(td) / "dense.safetensors"
        save_file({"input": arr_in, "weights": arr_w, "bias": arr_b}, str(p))
        loaded = load_file(str(p))
    expected = [[float(np.dot(arr_in, arr_w) + bias)]]
    observed = [[float(np.dot(loaded["input"], loaded["weights"]) + float(loaded["bias"][0]))]]
    ok = _allclose(expected, observed, abs_tol, rel_tol)
    return {
        "check": "safetensors_roundtrip",
        "status": "PASS" if ok else "FAIL",
        "classification": "E1" if ok else "E2",
        "reason": "SafeTensors roundtrip output matches expected tolerance."
        if ok
        else "SafeTensors roundtrip output mismatch.",
        "expected": expected,
        "observed": observed,
    }


def _check_canonical_json_stability(model_ir: dict[str, Any]) -> dict[str, Any]:
    obj_a = {"z": 3, "a": model_ir, "m": {"b": 2, "a": 1}}
    obj_b = {"m": {"a": 1, "b": 2}, "a": model_ir, "z": 3}
    s_a = json.dumps(obj_a, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    s_b = json.dumps(obj_b, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    ok = s_a == s_b
    return {
        "check": "canonical_json_stability",
        "status": "PASS" if ok else "FAIL",
        "classification": "E0" if ok else "E2",
        "reason": "Canonical JSON bytes are stable under key reorder." if ok else "Canonical JSON bytes differ.",
        "sha256_a": hashlib.sha256(s_a.encode("utf-8")).hexdigest(),
        "sha256_b": hashlib.sha256(s_b.encode("utf-8")).hexdigest(),
    }


def _check_canonical_cbor_stability(model_ir: dict[str, Any]) -> dict[str, Any]:
    obj_a = {"z": 3, "a": model_ir, "m": {"b": 2, "a": 1}}
    obj_b = {"m": {"a": 1, "b": 2}, "a": model_ir, "z": 3}
    c_a = encode_canonical(obj_a)
    c_b = encode_canonical(obj_b)
    ok = c_a == c_b
    return {
        "check": "canonical_cbor_stability",
        "status": "PASS" if ok else "FAIL",
        "classification": "E0" if ok else "E2",
        "reason": "Canonical CBOR bytes are stable under key reorder." if ok else "Canonical CBOR bytes differ.",
        "sha256_a": hashlib.sha256(c_a).hexdigest(),
        "sha256_b": hashlib.sha256(c_b).hexdigest(),
        "hex_len": len(encode_canonical_hex(obj_a)),
    }


def _runtime_meta() -> dict[str, Any]:
    meta: dict[str, Any] = {
        "platform": platform.platform(),
        "kernel": platform.release(),
        "python": platform.python_version(),
        "timestamp_utc": datetime.now(UTC).isoformat(),
    }
    for pkg in ("onnx", "onnxruntime", "safetensors"):
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
    parser = argparse.ArgumentParser(description="Milestone 22 artifact and serialization portability.")
    parser.add_argument("--abs-tol", type=float, default=1e-6)
    parser.add_argument("--rel-tol", type=float, default=1e-6)
    parser.add_argument(
        "--output-dir",
        default=str(ROOT / "evidence" / "repro" / "milestone-22-artifact-portability"),
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

    checks = [
        _check_onnx_roundtrip(inputs, weights, bias, args.abs_tol, args.rel_tol),
        _check_safetensors_roundtrip(inputs, weights, bias, args.abs_tol, args.rel_tol),
        _check_canonical_json_stability(model_ir),
        _check_canonical_cbor_stability(model_ir),
    ]

    statuses = [c["status"] for c in checks]
    if any(s == "FAIL" for s in statuses):
        overall_status, overall_class, overall_reason = (
            "FAIL",
            "E2",
            "At least one artifact portability check failed.",
        )
    elif any(s == "BLOCKED" for s in statuses):
        overall_status, overall_class, overall_reason = (
            "BLOCKED",
            "E2",
            "At least one artifact portability check is blocked.",
        )
    else:
        overall_status = "PASS"
        overall_class = "E0" if all(c["classification"] == "E0" for c in checks) else "E1"
        overall_reason = "All artifact portability checks pass."

    report = {
        "milestone": 22,
        "profile": "artifact_portability",
        "status": overall_status,
        "classification": overall_class,
        "reason": overall_reason,
        "checks": checks,
        "meta": {"abs_tol": args.abs_tol, "rel_tol": args.rel_tol, **_runtime_meta()},
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "repro-classification.json").write_text(
        json.dumps(
            {
                "milestone": 22,
                "profile": "artifact_portability",
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
                        "pair": "artifact_portability",
                        "status": overall_status,
                        "classification": overall_class,
                        "reason": overall_reason,
                        "checks": [c["check"] for c in checks],
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
            {"milestone": 22, "check_count": len(checks), "status": overall_status},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (out_dir / "device-matrix.json").write_text(
        json.dumps(
            {"note": "Milestone 22 focuses on artifact formats and serialization determinism."},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (out_dir / "os-matrix.json").write_text(
        json.dumps(
            {"note": "Milestone 22 is host-local artifact portability validation."},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (out_dir / "language-matrix.json").write_text(
        json.dumps(
            {"note": "Milestone 22 validates portable artifacts consumable across language lanes."},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (out_dir / "library-matrix.json").write_text(
        json.dumps(
            {"note": "Milestone 22 validates ONNX + SafeTensors + canonical JSON/CBOR contracts."},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    gaps = ["# Portability Gaps (Milestone 22)", ""]
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
                "# Milestone 22: Artifact and Serialization Portability",
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
        "# Known Limitations (Milestone 22)\n\n"
        "- SafeTensors lane requires `safetensors` package in the active environment.\n"
        "- ONNX lane requires `onnx` + `onnxruntime` + `numpy` packages.\n",
        encoding="utf-8",
    )
    (out_dir / "milestone.json").write_text(
        json.dumps(
            {
                "milestone": 22,
                "slug": "artifact-portability",
                "owner": "Astrocytech/Glyphser",
                "target_date": "2026-12-03",
                "dependencies": [21],
                "profiles": ["artifact_portability"],
                "result": overall_status,
                "classification": overall_class,
                "evidence_dir": "evidence/repro/milestone-22-artifact-portability/",
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
