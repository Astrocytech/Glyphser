#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from runtime.glyphser.backend.load_driver import load_driver  # noqa: E402
from runtime.glyphser.model.model_ir_executor import execute  # noqa: E402
from tooling.lib.path_config import fixtures_root  # noqa: E402

SUPPORTED_ROUTES = ["pytorch_cpu", "pytorch_gpu", "keras_cpu", "keras_gpu"]
WAIVER_ADR = "evidence/repro/decisions/ADR-2026-03-01-m12-resource-gap-temporary-waiver.md"


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


def _runtime_meta() -> dict[str, Any]:
    return {
        "platform": platform.platform(),
        "kernel": platform.release(),
        "python": platform.python_version(),
        "timestamp_utc": datetime.now(UTC).isoformat(),
    }


def _run_direct(driver_id: str, model_ir: dict[str, Any], inputs: list[float]) -> dict[str, Any]:
    return execute(
        {
            "ir_dag": model_ir,
            "input_data": {"input": inputs},
            "driver_id": driver_id,
            "mode": "forward",
            "replay_token": "milestone-17-universal-driver-v1",
            "tmmu_context": {"arena_config": {"default": {"capacity_bytes": 1_000_000, "alignment_bytes": 64}}},
        }
    )


def _run_universal(route: str, model_ir: dict[str, Any], inputs: list[float]) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        route_info = load_driver({"driver_id": "universal_driver", "universal_route": route})
    except Exception as exc:
        return (
            {"status": "ERROR", "selected_route": route, "error": {"code_id": "UNIVERSAL_ROUTE_UNAVAILABLE", "message": str(exc)}},
            {"error": {"code_id": "UNIVERSAL_ROUTE_UNAVAILABLE", "message": str(exc)}},
        )
    result = execute(
        {
            "ir_dag": model_ir,
            "input_data": {"input": inputs},
            "driver_id": "universal_driver",
            "universal_route": route,
            "mode": "forward",
            "replay_token": "milestone-17-universal-driver-v1",
            "tmmu_context": {"arena_config": {"default": {"capacity_bytes": 1_000_000, "alignment_bytes": 64}}},
        }
    )
    return route_info, result


def main() -> int:
    parser = argparse.ArgumentParser(description="Milestone 17 universal driver v1 reproducibility checks.")
    parser.add_argument("--abs-tol", type=float, default=1e-6)
    parser.add_argument("--rel-tol", type=float, default=1e-6)
    parser.add_argument(
        "--output-dir",
        default=str(ROOT / "evidence" / "repro" / "milestone-17-universal-driver-v1"),
    )
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    fixtures = fixtures_root() / "hello-core"
    dataset = [json.loads(line) for line in (fixtures / "tiny_synth_dataset.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    model_ir = json.loads((fixtures / "model_ir.json").read_text(encoding="utf-8"))
    inputs = dataset[0]["x"]

    pair_rows: list[dict[str, Any]] = []
    route_rows: list[dict[str, Any]] = []
    normalization_rows: list[dict[str, Any]] = []

    for route in SUPPORTED_ROUTES:
        direct = _run_direct(route, model_ir, inputs)
        route_info, universal = _run_universal(route, model_ir, inputs)
        if "error" in direct or "error" in universal:
            pair_rows.append(
                {
                    "pair": f"universal:{route}__vs__direct:{route}",
                    "status": "BLOCKED",
                    "classification": "E2",
                    "reason": "Direct or universal execution is blocked.",
                    "direct_result": direct,
                    "universal_result": universal,
                }
            )
            route_rows.append({"route": route, "status": "BLOCKED", "selected_route": route_info.get("selected_route", "")})
            normalization_rows.append({"route": route, "status": "BLOCKED"})
            continue

        outputs_equal = direct.get("outputs") == universal.get("outputs")
        fp_equal = direct.get("execution_fp") == universal.get("execution_fp")
        if outputs_equal and fp_equal:
            status, cls, reason = "PASS", "E0", "Exact output and execution fingerprint match."
        elif _allclose(direct.get("outputs"), universal.get("outputs"), args.abs_tol, args.rel_tol):
            status, cls, reason = "PASS", "E1", "Outputs within tolerance; runtime fingerprint differs."
        else:
            status, cls, reason = "FAIL", "E2", "Outputs diverge beyond tolerance."

        pair_rows.append(
            {
                "pair": f"universal:{route}__vs__direct:{route}",
                "status": status,
                "classification": cls,
                "reason": reason,
                "direct_result": direct,
                "universal_result": universal,
            }
        )
        route_rows.append(
            {
                "route": route,
                "status": "PASS" if route_info.get("selected_route") == route else "FAIL",
                "selected_route": route_info.get("selected_route"),
                "routing_policy": route_info.get("routing_policy", {}),
            }
        )
        expected_keys = {"outputs", "execution_fp", "tmmu_state_next", "rng_state_next"}
        direct_keys = set(direct.keys())
        universal_keys = set(universal.keys())
        normalization_rows.append(
            {
                "route": route,
                "status": "PASS" if direct_keys == universal_keys == expected_keys else "FAIL",
                "direct_keys": sorted(direct_keys),
                "universal_keys": sorted(universal_keys),
                "expected_keys": sorted(expected_keys),
            }
        )

    fallback_policy = {
        "driver_id": "universal_driver",
        "version": "v1",
        "rules": [
            {"rule": "explicit_route", "behavior": "Route exactly to universal_route if supported."},
            {"rule": "framework_preference", "behavior": "Prefer pytorch (default) or keras with gpu-first by default."},
            {"rule": "fallback", "behavior": "If preferred route is unavailable, fallback deterministically by ordered candidate list."},
            {"rule": "unsupported_language_route", "behavior": "Reject java_cpu and rust_cpu with deterministic ValueError."},
        ],
    }

    statuses = [p["status"] for p in pair_rows] + [r["status"] for r in route_rows] + [n["status"] for n in normalization_rows]
    if any(s == "FAIL" for s in statuses):
        overall_status, overall_class, overall_reason = "FAIL", "E2", "At least one universal-driver check failed."
    elif any(s == "BLOCKED" for s in statuses):
        overall_status, overall_class, overall_reason = "BLOCKED", "E2", "At least one universal-driver check is blocked."
    else:
        overall_status = "PASS"
        overall_class = "E0" if all(p["classification"] == "E0" for p in pair_rows) else "E1"
        overall_reason = "Universal driver route, parity, and normalization checks pass."

    report = {
        "milestone": 17,
        "profile": "universal_driver_v1",
        "status": overall_status,
        "classification": overall_class,
        "reason": overall_reason,
        "pairs": pair_rows,
        "route_matrix": route_rows,
        "normalization_parity": normalization_rows,
        "fallback_policy": fallback_policy,
        "meta": {"abs_tol": args.abs_tol, "rel_tol": args.rel_tol, **_runtime_meta()},
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "repro-classification.json").write_text(
        json.dumps(
            {
                "milestone": 17,
                "profile": "universal_driver_v1",
                "classification": overall_class,
                "status": overall_status,
                "reason": overall_reason,
                "abs_tol": args.abs_tol,
                "rel_tol": args.rel_tol,
                "excluded_operators": [],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (out_dir / "pair-matrix.json").write_text(json.dumps({"pairs": pair_rows}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "route-matrix.json").write_text(json.dumps({"routes": route_rows}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "normalization-parity.json").write_text(
        json.dumps({"normalization_parity": normalization_rows}, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (out_dir / "fallback-policy.json").write_text(json.dumps(fallback_policy, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "env-matrix.json").write_text(json.dumps(report["meta"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "coverage-summary.json").write_text(
        json.dumps(
            {
                "milestone": 17,
                "supported_routes": SUPPORTED_ROUTES,
                "status": overall_status,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
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
    (out_dir / "waivers.json").write_text(json.dumps({"waivers": waivers}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    conformance_hashes: dict[str, Any] = {"status": overall_status}
    results_path = ROOT / "evidence" / "conformance" / "results" / "latest.json"
    report_path = ROOT / "evidence" / "conformance" / "reports" / "latest.json"
    if results_path.exists():
        conformance_hashes["conformance_results"] = {"path": "evidence/conformance/results/latest.json", "sha256": _sha256_file(results_path)}
    if report_path.exists():
        conformance_hashes["conformance_report"] = {"path": "evidence/conformance/reports/latest.json", "sha256": _sha256_file(report_path)}
    (out_dir / "conformance-hashes.json").write_text(json.dumps(conformance_hashes, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "summary.md").write_text(
        "\n".join(
            [
                "# Milestone 17: Universal Driver v1",
                "",
                f"Status: {overall_status}",
                f"Classification: {overall_class}",
                f"Reason: {overall_reason}",
                "",
                "Routes:",
                "- pytorch_cpu",
                "- pytorch_gpu",
                "- keras_cpu",
                "- keras_gpu",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (out_dir / "known-limitations.md").write_text(
        "# Known Limitations (Milestone 17)\n\n"
        "- Universal driver currently routes only runtime-native adapters: pytorch/keras/reference.\n"
        "- java_cpu and rust_cpu are deterministic rejection routes in v1 policy.\n",
        encoding="utf-8",
    )
    (out_dir / "milestone.json").write_text(
        json.dumps(
            {
                "milestone": 17,
                "slug": "universal-driver-v1",
                "owner": "Astrocytech/Glyphser",
                "target_date": "2026-08-31",
                "dependencies": [16],
                "waiver_dependencies": [12],
                "profiles": ["universal_driver", *SUPPORTED_ROUTES],
                "result": overall_status,
                "classification": overall_class,
                "evidence_dir": "evidence/repro/milestone-17-universal-driver-v1/",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print(json.dumps({"status": overall_status, "classification": overall_class, "reason": overall_reason}, indent=2, sort_keys=True))
    return 0 if overall_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
