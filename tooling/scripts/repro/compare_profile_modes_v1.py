#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import platform
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from runtime.glyphser.backend.load_driver import load_driver
from runtime.glyphser.model.model_ir_executor import execute
from tooling.lib.path_config import fixtures_root

ROOT = Path(__file__).resolve().parents[3]
RUN_MARKER = "run-marker"


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


def _run_direct(route: str, model_ir: dict[str, Any], inputs: list[float]) -> dict[str, Any]:
    return execute(
        {
            "ir_dag": model_ir,
            "input_data": {"input": inputs},
            "driver_id": route,
            "mode": "forward",
            "replay_token": RUN_MARKER,
            "tmmu_context": {"arena_config": {"default": {"capacity_bytes": 1_000_000, "alignment_bytes": 64}}},
        }
    )


def _run_universal(
    req: dict[str, Any], model_ir: dict[str, Any], inputs: list[float]
) -> tuple[dict[str, Any], dict[str, Any]]:
    route_info = load_driver({"driver_id": "universal_driver", **req})
    result = execute(
        {
            "ir_dag": model_ir,
            "input_data": {"input": inputs},
            "driver_id": "universal_driver",
            **req,
            "mode": "forward",
            "replay_token": RUN_MARKER,
            "tmmu_context": {"arena_config": {"default": {"capacity_bytes": 1_000_000, "alignment_bytes": 64}}},
        }
    )
    return route_info, result


def _status_from_pair(
    direct: dict[str, Any], universal: dict[str, Any], abs_tol: float, rel_tol: float
) -> tuple[str, str, str]:
    if "error" in direct or "error" in universal:
        return "BLOCKED", "E2", "One side returned runtime error."
    if direct.get("outputs") == universal.get("outputs") and direct.get("execution_fp") == universal.get(
        "execution_fp"
    ):
        return "PASS", "E0", "Exact output and execution fingerprint match."
    if _allclose(direct.get("outputs"), universal.get("outputs"), abs_tol, rel_tol):
        return "PASS", "E1", "Outputs within tolerance."
    return "FAIL", "E2", "Outputs diverge beyond tolerance."


def main() -> int:
    parser = argparse.ArgumentParser(description="Milestone 17A optional universality profile modes.")
    parser.add_argument("--abs-tol", type=float, default=1e-6)
    parser.add_argument("--rel-tol", type=float, default=1e-6)
    parser.add_argument(
        "--output-dir",
        default=str(ROOT / "evidence" / "repro" / "milestone-17a-profile-modes"),
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

    mode_cases: list[tuple[str, dict[str, Any]]] = [
        (
            "strict_universal_cpu",
            {"profile_mode": "strict_universal", "universal_route": "pytorch_cpu"},
        ),
        (
            "balanced_default",
            {
                "profile_mode": "balanced",
                "universal_framework": "pytorch",
                "universal_prefer_gpu": True,
            },
        ),
        (
            "optimized_native_default",
            {
                "profile_mode": "optimized_native",
                "universal_framework": "pytorch",
                "universal_prefer_gpu": True,
            },
        ),
        (
            "pinned_profile_v1",
            {"profile_mode": "pinned_profile", "profile_id": "universal_v1"},
        ),
    ]

    pair_rows: list[dict[str, Any]] = []
    mode_rows: list[dict[str, Any]] = []
    policy_rows: list[dict[str, Any]] = []

    for case_id, req in mode_cases:
        try:
            route_info, universal = _run_universal(req, model_ir, inputs)
            route = route_info.get("selected_route", "")
            direct = (
                _run_direct(route, model_ir, inputs)
                if route
                else {
                    "error": {
                        "code_id": "ROUTE_MISSING",
                        "message": "selected_route missing",
                    }
                }
            )
            status, cls, reason = _status_from_pair(direct, universal, args.abs_tol, args.rel_tol)
            pair_rows.append(
                {
                    "pair": f"mode:{case_id}__vs__direct:{route or 'none'}",
                    "status": status,
                    "classification": cls,
                    "reason": reason,
                    "direct_result": direct,
                    "universal_result": universal,
                    "route_info": route_info,
                }
            )
            mode_rows.append(
                {
                    "case_id": case_id,
                    "status": status,
                    "selected_route": route,
                    "profile_mode": route_info.get("routing_policy", {}).get("profile_mode", ""),
                    "profile_id": route_info.get("routing_policy", {}).get("profile_id", ""),
                }
            )
            policy_rows.append(
                {
                    "case_id": case_id,
                    "request": req,
                    "routing_policy": route_info.get("routing_policy", {}),
                }
            )
        except Exception as exc:
            pair_rows.append(
                {
                    "pair": f"mode:{case_id}__vs__direct:none",
                    "status": "BLOCKED",
                    "classification": "E2",
                    "reason": f"mode execution blocked: {exc}",
                }
            )
            mode_rows.append({"case_id": case_id, "status": "BLOCKED", "selected_route": ""})
            policy_rows.append({"case_id": case_id, "request": req, "error": str(exc)})

    # Deterministic rejection behavior check.
    rejection_rows: list[dict[str, Any]] = []
    for bad_route in ("java_cpu", "rust_cpu"):
        try:
            _ = load_driver(
                {
                    "driver_id": "universal_driver",
                    "profile_mode": "balanced",
                    "universal_route": bad_route,
                }
            )
            rejection_rows.append(
                {
                    "route": bad_route,
                    "status": "FAIL",
                    "reason": "Unsupported route unexpectedly accepted.",
                }
            )
        except Exception as exc:
            rejection_rows.append(
                {
                    "route": bad_route,
                    "status": "PASS",
                    "reason": str(exc),
                }
            )

    statuses = [p["status"] for p in pair_rows] + [r["status"] for r in rejection_rows]
    if any(s == "FAIL" for s in statuses):
        overall_status, overall_class, overall_reason = (
            "FAIL",
            "E2",
            "At least one profile-mode check failed.",
        )
    elif any(s == "BLOCKED" for s in statuses):
        overall_status, overall_class, overall_reason = (
            "BLOCKED",
            "E2",
            "At least one profile-mode check is blocked.",
        )
    else:
        overall_status = "PASS"
        overall_class = "E0" if all(p["classification"] == "E0" for p in pair_rows) else "E1"
        overall_reason = "All profile modes route deterministically and preserve parity."

    report = {
        "milestone": "17A",
        "profile": "optional_universality_profile_modes",
        "status": overall_status,
        "classification": overall_class,
        "reason": overall_reason,
        "pairs": pair_rows,
        "profile_mode_matrix": mode_rows,
        "rejection_checks": rejection_rows,
        "profile_mode_policy": policy_rows,
        "meta": {"abs_tol": args.abs_tol, "rel_tol": args.rel_tol, **_runtime_meta()},
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "repro-classification.json").write_text(
        json.dumps(
            {
                "milestone": "17A",
                "profile": "optional_universality_profile_modes",
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
    (out_dir / "pair-matrix.json").write_text(
        json.dumps({"pairs": pair_rows}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "profile-mode-matrix.json").write_text(
        json.dumps(
            {"profile_modes": mode_rows, "rejections": rejection_rows},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (out_dir / "profile-mode-policy.json").write_text(
        json.dumps({"policies": policy_rows}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "env-matrix.json").write_text(
        json.dumps(report["meta"], indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (out_dir / "coverage-summary.json").write_text(
        json.dumps(
            {
                "milestone": "17A",
                "profile_modes": sorted({m["profile_mode"] for m in mode_rows if m.get("profile_mode")}),
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
    (out_dir / "summary.md").write_text(
        "\n".join(
            [
                "# Milestone 17A: Optional Universality Profile Modes",
                "",
                f"Status: {overall_status}",
                f"Classification: {overall_class}",
                f"Reason: {overall_reason}",
                "",
                "Profile modes validated:",
                "- strict_universal",
                "- balanced",
                "- optimized_native",
                "- pinned_profile",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (out_dir / "known-limitations.md").write_text(
        "# Known Limitations (Milestone 17A)\n\n"
        "- Pinned profiles are currently static in code and should be migrated to policy "
        "registry in later hardening.\n",
        encoding="utf-8",
    )
    (out_dir / "milestone.json").write_text(
        json.dumps(
            {
                "milestone": "17A",
                "slug": "profile-modes",
                "owner": "Astrocytech/Glyphser",
                "target_date": "2026-09-01",
                "dependencies": [17],
                "profiles": ["universal_driver"],
                "result": overall_status,
                "classification": overall_class,
                "evidence_dir": "evidence/repro/milestone-17a-profile-modes/",
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
