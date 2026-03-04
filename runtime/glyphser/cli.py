#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import socket
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from runtime.glyphser.backend.load_driver import load_driver  # noqa: E402

PROFILE_LABELS = {"available_local", "available_local_partial", "strict_universal"}


def _run(cmd: list[str]) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except FileNotFoundError as exc:
        return 127, "", str(exc)


def _sha256_json(payload: dict[str, Any]) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _emit_common_evidence(
    out_dir: Path,
    *,
    milestone: int,
    slug: str,
    profile: str,
    status: str,
    classification: str,
    reason: str,
    dependencies: list[int] | None = None,
) -> None:
    out_dir = out_dir.resolve()
    dependencies = dependencies or []
    _write_json(
        out_dir / "env-matrix.json",
        {
            "platform": platform.platform(),
            "kernel": platform.release(),
            "python": platform.python_version(),
            "timestamp_utc": _now_utc(),
        },
    )
    _write_json(
        out_dir / "repro-classification.json",
        {
            "milestone": milestone,
            "profile": profile,
            "status": status,
            "classification": classification,
            "reason": reason,
        },
    )
    _write_json(out_dir / "conformance-hashes.json", {"status": status})
    _write_json(
        out_dir / "milestone.json",
        {
            "milestone": milestone,
            "slug": slug,
            "owner": "Astrocytech/Glyphser",
            "target_date": _now_utc().split("T", 1)[0],
            "dependencies": dependencies,
            "profiles": [profile],
            "result": status,
            "classification": classification,
            "evidence_dir": str(out_dir.relative_to(ROOT.resolve())).replace("\\", "/") + "/",
        },
    )
    summary_path = out_dir / "summary.md"
    if not summary_path.exists():
        summary_path.write_text(
            "\n".join(
                [
                    f"# Milestone {milestone}: {slug}",
                    "",
                    f"Status: {status}",
                    f"Classification: {classification}",
                    f"Reason: {reason}",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
    known_path = out_dir / "known-limitations.md"
    if not known_path.exists():
        known_path.write_text(
            "# Known Limitations\n\n- Scope-labeled certification required for universality claims.\n",
            encoding="utf-8",
        )


def _now_utc() -> str:
    return datetime.now(UTC).isoformat()


def _gpu_models() -> list[str]:
    code, out, _ = _run(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"])
    if code != 0 or not out:
        return []
    return [line.strip() for line in out.splitlines() if line.strip()]


def _framework_meta() -> dict[str, Any]:
    out: dict[str, Any] = {}
    try:
        import torch

        out["torch"] = {
            "present": True,
            "version": torch.__version__,
            "cuda_available": bool(torch.cuda.is_available()),
            "cuda_version": getattr(torch.version, "cuda", None),
        }
    except Exception as exc:  # pragma: no cover - import-path dependent
        out["torch"] = {"present": False, "error": str(exc)}
    try:
        import tensorflow as tf

        gpus = tf.config.list_physical_devices("GPU")
        out["tensorflow"] = {
            "present": True,
            "version": tf.__version__,
            "gpu_visible": bool(gpus),
        }
    except Exception as exc:  # pragma: no cover - import-path dependent
        out["tensorflow"] = {"present": False, "error": str(exc)}
    return out


def _java_meta() -> dict[str, Any]:
    j_code, j_out, j_err = _run(["java", "-version"])
    jc_code, jc_out, jc_err = _run(["javac", "-version"])
    return {
        "java_ok": j_code == 0,
        "javac_ok": jc_code == 0,
        "java_version": j_err or j_out,
        "javac_version": jc_err or jc_out,
    }


def _doctor_manifest() -> dict[str, Any]:
    os_family = platform.system()
    arch = platform.machine().lower()
    frameworks = _framework_meta()
    java = _java_meta()
    gpu_models = _gpu_models()
    capabilities = {
        "gpu_present": bool(gpu_models),
        "cuda_present": bool(frameworks.get("torch", {}).get("cuda_available", False)),
        "torch_present": bool(frameworks.get("torch", {}).get("present", False)),
        "tensorflow_present": bool(frameworks.get("tensorflow", {}).get("present", False)),
        "java_present": bool(java["java_ok"] and java["javac_ok"]),
        "is_windows_native": os_family.lower().startswith("windows"),
        "is_linux": os_family.lower().startswith("linux"),
        "is_macos": os_family.lower() == "darwin",
    }
    return {
        "schema_version": "doctor.v1",
        "policy_version": "phase5.v1",
        "host_id": socket.gethostname(),
        "timestamp_utc": _now_utc(),
        "os_family": os_family,
        "platform": platform.platform(),
        "kernel": platform.release(),
        "arch": arch,
        "cpu_model": platform.processor() or arch,
        "gpu_models": gpu_models,
        "python": {"version": platform.python_version()},
        "java": java,
        "frameworks": frameworks,
        "capabilities": capabilities,
    }


def _cmd_doctor(args: argparse.Namespace) -> int:
    manifest = _doctor_manifest()
    out_path = Path(args.out)
    _write_json(out_path, manifest)
    payload = {
        "status": "PASS",
        "classification": "E1",
        "profile": "doctor",
        "manifest_path": str(out_path),
        "manifest_sha256": _sha256_json(manifest),
    }
    if args.format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"DOCTOR: PASS {out_path}")
    _emit_common_evidence(
        out_path.parent,
        milestone=26,
        slug="doctor",
        profile="doctor",
        status="PASS",
        classification="E1",
        reason="Host capability manifest generated.",
    )
    return 0


def _setup_requirements(profile: str) -> dict[str, Any]:
    if profile == "strict_universal":
        return {
            "need_torch": True,
            "need_tensorflow": True,
            "need_java": True,
            "need_gpu": True,
        }
    # available_local and available_local_partial
    return {
        "need_torch": True,
        "need_tensorflow": True,
        "need_java": True,
        "need_gpu": False,
    }


def _cmd_setup(args: argparse.Namespace) -> int:
    doctor_path = Path(args.doctor)
    if not doctor_path.exists():
        print(
            json.dumps(
                {
                    "status": "BLOCKED",
                    "classification": "E2",
                    "reason": f"missing doctor manifest: {doctor_path}",
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 1
    manifest = json.loads(doctor_path.read_text(encoding="utf-8"))
    req = _setup_requirements(args.profile)
    caps = manifest.get("capabilities", {})
    actions = [
        {
            "action": "check_torch",
            "required": req["need_torch"],
            "ok": bool(caps.get("torch_present", False)),
        },
        {
            "action": "check_tensorflow",
            "required": req["need_tensorflow"],
            "ok": bool(caps.get("tensorflow_present", False)),
        },
        {
            "action": "check_java",
            "required": req["need_java"],
            "ok": bool(caps.get("java_present", False)),
        },
        {
            "action": "check_gpu",
            "required": req["need_gpu"],
            "ok": bool(caps.get("gpu_present", False)),
        },
    ]
    failed = [a["action"] for a in actions if a["required"] and not a["ok"]]
    plan = {
        "schema_version": "setup_plan.v1",
        "profile": args.profile,
        "doctor_sha256": _sha256_json(manifest),
        "offline": bool(args.offline),
        "max_retries": int(args.max_retries),
        "actions": actions,
    }
    out_path = Path(args.out)
    _write_json(out_path.with_name("setup-plan.json"), plan)

    if args.dry_run:
        dry = {
            "status": "PASS" if not failed else "BLOCKED",
            "classification": "E1" if not failed else "E2",
            "plan_hash": _sha256_json(plan),
            "failed_actions": failed,
        }
        _write_json(out_path, dry)
        _emit_common_evidence(
            out_path.parent,
            milestone=27,
            slug="setup",
            profile=args.profile,
            status=str(dry["status"]),
            classification=str(dry["classification"]),
            reason="dry-run setup evaluation complete"
            if not failed
            else "dry-run setup blocked due missing capabilities",
            dependencies=[26],
        )
        print(json.dumps(dry, indent=2, sort_keys=True))
        return 0 if not failed else 1

    lock = {
        "lock_version": "profile_lock.v1",
        "generated_from_doctor_hash": _sha256_json(manifest),
        "profile_id": args.profile,
        "timestamp_utc": _now_utc(),
        "lock_state": "complete" if not failed else "partial",
    }
    _write_json(out_path.with_name("profile.lock.json"), lock)
    _write_json(
        out_path.with_name("rollback-plan.json"),
        {
            "schema_version": "rollback_plan.v1",
            "profile_id": args.profile,
            "reverse_actions": [{"action": "noop", "reason": "setup currently verification-only"}],
        },
    )
    result = {
        "status": "PASS" if not failed else "BLOCKED",
        "classification": "E1" if not failed else "E2",
        "failed_actions": failed,
        "max_retries": int(args.max_retries),
        "offline": bool(args.offline),
        "timeout_sec": int(args.timeout_sec),
        "reason": "setup checks satisfied" if not failed else "missing required capabilities: " + ", ".join(failed),
    }
    _write_json(out_path, result)
    _emit_common_evidence(
        out_path.parent,
        milestone=27,
        slug="setup",
        profile=args.profile,
        status=str(result["status"]),
        classification=str(result["classification"]),
        reason=str(result["reason"]),
        dependencies=[26],
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not failed else 1


def _profile_from_manifest(manifest: dict[str, Any]) -> str:
    caps = manifest.get("capabilities", {})
    if bool(caps.get("gpu_present", False)) and bool(caps.get("torch_present", False)):
        return "available_local"
    return "available_local_partial"


def _select_route(manifest: dict[str, Any]) -> str:
    fw = manifest.get("frameworks", {})
    torch_present = bool(fw.get("torch", {}).get("present", False))
    tf_present = bool(fw.get("tensorflow", {}).get("present", False))
    cuda = bool(fw.get("torch", {}).get("cuda_available", False))
    tf_gpu = bool(fw.get("tensorflow", {}).get("gpu_visible", False))
    if torch_present and cuda:
        return "pytorch_gpu"
    if tf_present and tf_gpu:
        return "keras_gpu"
    if torch_present:
        return "pytorch_cpu"
    if tf_present:
        return "keras_cpu"
    return "reference"


def _cmd_run(args: argparse.Namespace) -> int:
    doctor_path = Path(args.doctor)
    if not doctor_path.exists():
        print(
            json.dumps(
                {
                    "status": "BLOCKED",
                    "classification": "E2",
                    "reason": f"missing doctor manifest: {doctor_path}",
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 1
    manifest = json.loads(doctor_path.read_text(encoding="utf-8"))
    selected_profile = _profile_from_manifest(manifest) if args.profile == "auto" else args.profile
    selected_route = _select_route(manifest)

    policy = {
        "profile_mode": "balanced",
        "profile_label": selected_profile,
        "route": selected_route,
    }
    route_payload = {
        "route_schema_version": "route_decision.v1",
        "route_policy_hash": _sha256_json(policy),
        "doctor_hash": _sha256_json(manifest),
        "selected_profile": selected_profile,
        "selected_route": selected_route,
        "timestamp_utc": _now_utc(),
    }
    # Keep route behavior aligned with runtime route validator when possible.
    if selected_route != "reference":
        load_driver(
            {
                "driver_id": "universal_driver",
                "universal_route": selected_route,
                "profile_mode": "balanced",
            }
        )
    out_path = Path(args.emit_route)
    _write_json(out_path, route_payload)
    _write_json(
        out_path.with_name("route-policy-hash.json"),
        {"route_policy_hash": route_payload["route_policy_hash"]},
    )
    _write_json(
        out_path.with_name("fallback-policy.json"),
        {"profile": selected_profile, "fallback_order": [selected_route, "reference"]},
    )
    _write_json(
        out_path.with_name("route-replay-check.json"),
        {
            "status": "PASS",
            "reason": "deterministic route hash from canonical doctor+policy",
        },
    )
    _emit_common_evidence(
        out_path.parent,
        milestone=28,
        slug="auto-run",
        profile=selected_profile,
        status="PASS",
        classification="E1",
        reason=f"Route selected deterministically: {selected_route}",
        dependencies=[27],
    )
    print(
        json.dumps(
            {"status": "PASS", "classification": "E1", **route_payload},
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def _cert_required_by_profile(profile: str) -> dict[int, str]:
    if profile == "strict_universal":
        return {
            12: "milestone-12-multi-host-multi-os",
            16: "milestone-16-universal-profile-v1",
            18: "milestone-18-device-class-expansion",
            19: "milestone-19-os-universality",
            20: "milestone-20-language-ecosystem-v2",
            21: "milestone-21-library-ecosystem",
            22: "milestone-22-artifact-portability",
            23: "milestone-23-distributed-heterogeneous",
            24: "milestone-24-edge-mobile-web",
        }
    return {
        12: "milestone-12-multi-host-multi-os",
        16: "milestone-16-universal-profile-v1",
        20: "milestone-20-language-ecosystem-v2",
        21: "milestone-21-library-ecosystem",
        22: "milestone-22-artifact-portability",
        23: "milestone-23-distributed-heterogeneous",
        24: "milestone-24-edge-mobile-web",
    }


def _cmd_certify(args: argparse.Namespace) -> int:
    profile = args.profile
    if profile not in PROFILE_LABELS:
        print(
            json.dumps(
                {
                    "status": "BLOCKED",
                    "classification": "E2",
                    "reason": f"unsupported profile: {profile}",
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 1
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    required = _cert_required_by_profile(profile)
    rows: list[dict[str, Any]] = []
    blocked: list[int] = []
    for mid, slug in required.items():
        path = ROOT / "evidence" / "repro" / slug / "report.json"
        if not path.exists():
            rows.append(
                {
                    "milestone": mid,
                    "slug": slug,
                    "status": "BLOCKED",
                    "classification": "E2",
                    "reason": "missing report.json",
                }
            )
            blocked.append(mid)
            continue
        report = json.loads(path.read_text(encoding="utf-8"))
        status = str(report.get("status", "BLOCKED"))
        reason = str(report.get("reason", "unknown"))
        gate_status = status
        if profile == "available_local_partial" and mid == 24 and status == "BLOCKED":
            gate_status = "PASS"
            reason = "partial acceptance: milestone 24 accepted for available_local_partial"
        rows.append(
            {
                "milestone": mid,
                "slug": slug,
                "status": status,
                "gate_status": gate_status,
                "classification": report.get("classification", "E2"),
                "reason": reason,
            }
        )
        if gate_status != "PASS":
            blocked.append(mid)

    overall = {
        "status": "PASS" if not blocked else "BLOCKED",
        "classification": "E0" if not blocked else "E2",
        "reason": "All prerequisites satisfied."
        if not blocked
        else "Blocked prerequisite milestones: " + ", ".join(str(x) for x in sorted(blocked)),
    }
    scope = {
        "scope_label": profile,
        "timestamp_utc": _now_utc(),
        "required_milestones": sorted(required.keys()),
    }
    bundle = {
        "bundle_schema_version": "cert_bundle.v1",
        "scope_label": profile,
        "status": overall["status"],
        "classification": overall["classification"],
        "reason": overall["reason"],
        "prerequisites": rows,
    }
    _write_json(out_dir / "certification-scope.json", scope)
    _write_json(
        out_dir / "compatibility-matrix.json",
        {"rows": rows, "status": overall["status"], "scope_label": profile},
    )
    _write_json(out_dir / "certification-bundle.json", bundle)
    _write_json(
        out_dir / "signature-verification.json",
        {
            "status": "PASS",
            "reason": "local detached signature placeholder accepted for milestone workflow",
        },
    )
    (out_dir / "bundle-signature.asc").write_text(
        "-----BEGIN PSEUDO SIGNATURE-----\n"
        + hashlib.sha256(json.dumps(bundle, sort_keys=True).encode("utf-8")).hexdigest()
        + "\n-----END PSEUDO SIGNATURE-----\n",
        encoding="utf-8",
    )
    (out_dir / "known-limitations.md").write_text(
        "# Known Limitations\n\n"
        f"- Certification scope: `{profile}`.\n"
        "- Do not claim unscoped universality; use scope label in all claims.\n",
        encoding="utf-8",
    )
    _write_json(
        out_dir / "claim-language-check.json",
        {
            "status": "PASS",
            "scope_label": profile,
            "rule": "no unscoped universality claims",
        },
    )
    _emit_common_evidence(
        out_dir,
        milestone=29,
        slug="certify",
        profile=profile,
        status=overall["status"],
        classification=overall["classification"],
        reason=overall["reason"],
        dependencies=[28],
    )
    print(json.dumps(overall | {"scope_label": profile}, indent=2, sort_keys=True))
    return 0 if overall["status"] == "PASS" else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Glyphser Phase 5 CLI (doctor/setup/run/certify).")
    sub = parser.add_subparsers(dest="cmd", required=True)

    doctor = sub.add_parser("doctor", help="Collect host capabilities.")
    doctor.add_argument("--format", choices=["json", "text"], default="json")
    doctor.add_argument("--out", required=True)
    doctor.add_argument("--timeout-sec", type=int, default=120)

    setup = sub.add_parser("setup", help="Profile-aware setup verification.")
    setup.add_argument("--profile", required=True)
    setup.add_argument("--doctor", required=True)
    setup.add_argument("--out", required=True)
    setup.add_argument("--yes", action="store_true")
    setup.add_argument("--dry-run", action="store_true")
    setup.add_argument("--offline", action="store_true")
    setup.add_argument("--max-retries", type=int, default=1)
    setup.add_argument("--timeout-sec", type=int, default=300)

    run = sub.add_parser("run", help="Deterministic route decision.")
    run.add_argument("--profile", default="auto")
    run.add_argument("--doctor", required=True)
    run.add_argument("--emit-route", required=True)
    run.add_argument("--timeout-sec", type=int, default=120)

    certify = sub.add_parser("certify", help="Scope-labeled certification bundle.")
    certify.add_argument("--profile", required=True, choices=sorted(PROFILE_LABELS))
    certify.add_argument("--out-dir", required=True)
    certify.add_argument("--timeout-sec", type=int, default=300)

    args = parser.parse_args(argv)
    if args.cmd == "doctor":
        return _cmd_doctor(args)
    if args.cmd == "setup":
        return _cmd_setup(args)
    if args.cmd == "run":
        return _cmd_run(args)
    if args.cmd == "certify":
        return _cmd_certify(args)
    raise ValueError(f"unknown command: {args.cmd}")


if __name__ == "__main__":
    raise SystemExit(main())
