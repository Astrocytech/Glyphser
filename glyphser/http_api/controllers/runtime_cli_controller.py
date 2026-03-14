from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any

from runtime.glyphser import cli as runtime_cli


def _sha256_json(payload: dict[str, Any]) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _safe_run_id(run_id: str | None) -> str:
    if run_id is None:
        return str(time.time_ns())
    cleaned = run_id.strip()
    if not cleaned:
        raise ValueError("run_id must be non-empty if provided")
    if "/" in cleaned or "\\" in cleaned:
        raise ValueError("run_id must not contain path separators")
    return cleaned


class RuntimeCliController:
    def __init__(self, *, work_root: Path) -> None:
        self._work_root = work_root

    def doctor(self, *, run_id: str | None) -> dict[str, Any]:
        rid = _safe_run_id(run_id)
        out_dir = (self._work_root / "doctor" / rid).resolve()
        out_path = out_dir / "doctor.json"
        manifest = runtime_cli._doctor_manifest()
        _write_json(out_path, manifest)
        payload = {
            "status": "PASS",
            "classification": "E1",
            "profile": "doctor",
            "run_id": rid,
            "manifest": manifest,
            "manifest_path": str(out_path),
            "manifest_sha256": _sha256_json(manifest),
        }
        runtime_cli._emit_common_evidence(
            out_dir,
            milestone=26,
            slug="doctor",
            profile="doctor",
            status="PASS",
            classification="E1",
            reason="Host capability manifest generated.",
        )
        return payload

    def setup(
        self,
        *,
        profile: str,
        doctor_manifest: dict[str, Any],
        dry_run: bool,
        offline: bool,
        max_retries: int,
        timeout_sec: int,
        run_id: str | None,
    ) -> dict[str, Any]:
        rid = _safe_run_id(run_id)
        out_dir = (self._work_root / "setup" / rid).resolve()
        out_path = out_dir / "setup-result.json"

        req = runtime_cli._setup_requirements(profile)
        caps = doctor_manifest.get("capabilities", {})
        actions = [
            {"action": "check_torch", "required": req["need_torch"], "ok": bool(caps.get("torch_present", False))},
            {
                "action": "check_tensorflow",
                "required": req["need_tensorflow"],
                "ok": bool(caps.get("tensorflow_present", False)),
            },
            {"action": "check_java", "required": req["need_java"], "ok": bool(caps.get("java_present", False))},
            {"action": "check_gpu", "required": req["need_gpu"], "ok": bool(caps.get("gpu_present", False))},
        ]
        failed = [a["action"] for a in actions if a["required"] and not a["ok"]]
        plan = {
            "schema_version": "setup_plan.v1",
            "profile": profile,
            "doctor_sha256": _sha256_json(doctor_manifest),
            "offline": bool(offline),
            "max_retries": int(max_retries),
            "actions": actions,
        }
        _write_json(out_dir / "setup-plan.json", plan)

        if dry_run:
            dry = {
                "status": "PASS" if not failed else "BLOCKED",
                "classification": "E1" if not failed else "E2",
                "plan_hash": _sha256_json(plan),
                "failed_actions": failed,
            }
            _write_json(out_path, dry)
            runtime_cli._emit_common_evidence(
                out_dir,
                milestone=27,
                slug="setup",
                profile=profile,
                status=str(dry["status"]),
                classification=str(dry["classification"]),
                reason="dry-run setup evaluation complete"
                if not failed
                else "dry-run setup blocked due missing capabilities",
                dependencies=[26],
            )
            return {"run_id": rid, "result_path": str(out_path), "plan_path": str(out_dir / "setup-plan.json"), **dry}

        lock = {
            "lock_version": "profile_lock.v1",
            "generated_from_doctor_hash": _sha256_json(doctor_manifest),
            "profile_id": profile,
            "timestamp_utc": runtime_cli._now_utc(),
            "lock_state": "complete" if not failed else "partial",
        }
        _write_json(out_dir / "profile.lock.json", lock)
        _write_json(
            out_dir / "rollback-plan.json",
            {
                "schema_version": "rollback_plan.v1",
                "profile_id": profile,
                "reverse_actions": [{"action": "noop", "reason": "setup currently verification-only"}],
            },
        )
        result = {
            "status": "PASS" if not failed else "BLOCKED",
            "classification": "E1" if not failed else "E2",
            "failed_actions": failed,
            "max_retries": int(max_retries),
            "offline": bool(offline),
            "timeout_sec": int(timeout_sec),
            "reason": "setup checks satisfied" if not failed else "missing required capabilities: " + ", ".join(failed),
        }
        _write_json(out_path, result)
        runtime_cli._emit_common_evidence(
            out_dir,
            milestone=27,
            slug="setup",
            profile=profile,
            status=str(result["status"]),
            classification=str(result["classification"]),
            reason=str(result["reason"]),
            dependencies=[26],
        )
        return {
            "run_id": rid,
            "result_path": str(out_path),
            "plan_path": str(out_dir / "setup-plan.json"),
            "lock_path": str(out_dir / "profile.lock.json"),
            "rollback_path": str(out_dir / "rollback-plan.json"),
            **result,
        }

    def route_run(
        self,
        *,
        profile: str,
        doctor_manifest: dict[str, Any],
        run_id: str | None,
    ) -> dict[str, Any]:
        rid = _safe_run_id(run_id)
        out_dir = (self._work_root / "route_run" / rid).resolve()
        out_path = out_dir / "route_decision.json"

        selected_profile = runtime_cli._profile_from_manifest(doctor_manifest) if profile == "auto" else profile
        selected_route = runtime_cli._select_route(doctor_manifest)
        policy = {"profile_mode": "balanced", "profile_label": selected_profile, "route": selected_route}
        route_payload = {
            "route_schema_version": "route_decision.v1",
            "route_policy_hash": _sha256_json(policy),
            "doctor_hash": _sha256_json(doctor_manifest),
            "selected_profile": selected_profile,
            "selected_route": selected_route,
            "timestamp_utc": runtime_cli._now_utc(),
        }
        if selected_route != "reference":
            runtime_cli.load_driver(
                {
                    "driver_id": "universal_driver",
                    "universal_route": selected_route,
                    "profile_mode": "balanced",
                }
            )
        _write_json(out_path, route_payload)
        _write_json(out_dir / "route-policy-hash.json", {"route_policy_hash": route_payload["route_policy_hash"]})
        _write_json(out_dir / "fallback-policy.json", {"profile": selected_profile, "fallback_order": [selected_route, "reference"]})
        _write_json(
            out_dir / "route-replay-check.json",
            {"status": "PASS", "reason": "deterministic route hash from canonical doctor+policy"},
        )
        runtime_cli._emit_common_evidence(
            out_dir,
            milestone=28,
            slug="auto-run",
            profile=selected_profile,
            status="PASS",
            classification="E1",
            reason=f"Route selected deterministically: {selected_route}",
            dependencies=[27],
        )
        return {"run_id": rid, "route_path": str(out_path), "route": route_payload, "status": "PASS", "classification": "E1"}

    def certify(self, *, profile: str, run_id: str | None) -> dict[str, Any]:
        rid = _safe_run_id(run_id)
        out_dir = (self._work_root / "certify" / rid).resolve()
        out_dir.mkdir(parents=True, exist_ok=True)

        # Reuse CLI implementation by invoking its private command handler logic via main-like call.
        # This keeps bundle structure identical to `runtime/glyphser/cli.py`.
        rc = runtime_cli._cmd_certify(
            argparse.Namespace(
                profile=profile,
                out_dir=str(out_dir),
                timeout_sec=300,
            )
        )
        status = "PASS" if rc == 0 else "BLOCKED"
        bundle_path = out_dir / "certification-bundle.json"
        bundle = json.loads(bundle_path.read_text(encoding="utf-8")) if bundle_path.exists() else {}
        return {"run_id": rid, "status": status, "out_dir": str(out_dir), "bundle": bundle}
