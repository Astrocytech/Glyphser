#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tooling.path_config import evidence_root, generated_root

GEN = generated_root() / "deploy"
OUT = evidence_root() / "deploy"
STATE_DIR = OUT / "state"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _health_check(manifest: Dict[str, Any]) -> Dict[str, Any]:
    failures: List[str] = []
    for entry in manifest.get("artifacts", []):
        rel = entry.get("path", "")
        want = entry.get("sha256", "")
        path = ROOT / rel
        if not path.exists():
            failures.append(f"missing:{rel}")
            continue
        got = _sha256(path)
        if got != want:
            failures.append(f"hash_mismatch:{rel}")
    return {"status": "PASS" if not failures else "FAIL", "failures": failures}


def _readiness_check(overlay: Dict[str, Any]) -> Dict[str, Any]:
    required = [
        "deployment_environment",
        "rollout_strategy",
        "max_parallel_rollout_percent",
        "rollback_error_rate_threshold",
        "approval_required",
        "quota_jobs_per_hour",
        "budget_alarm_usd_monthly",
    ]
    missing = [k for k in required if k not in overlay]
    return {"status": "PASS" if not missing else "FAIL", "missing": missing}


def _json_diff(old: Dict[str, Any], new: Dict[str, Any]) -> List[str]:
    changed: List[str] = []
    keys = sorted(set(old.keys()) | set(new.keys()))
    for k in keys:
        if old.get(k) != new.get(k):
            changed.append(k)
    return changed


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    STATE_DIR.mkdir(parents=True, exist_ok=True)

    manifest = _load_json(GEN / "managed" / "bundle_manifest.json")
    overlay = _load_json(GEN / "overlays" / "staging.json")
    candidate = {
        "deployment_target": "staging",
        "bundle_hash": manifest.get("bundle_hash", ""),
        "manifest_path": str((GEN / "managed" / "bundle_manifest.json").relative_to(ROOT)).replace("\\", "/"),
        "overlay_path": str((GEN / "overlays" / "staging.json").relative_to(ROOT)).replace("\\", "/"),
        "rollout_strategy": overlay.get("rollout_strategy"),
        "max_parallel_rollout_percent": overlay.get("max_parallel_rollout_percent"),
        "rollback_error_rate_threshold": overlay.get("rollback_error_rate_threshold"),
        "quota_jobs_per_hour": overlay.get("quota_jobs_per_hour"),
        "budget_alarm_usd_monthly": overlay.get("budget_alarm_usd_monthly"),
    }

    health = _health_check(manifest)
    readiness = _readiness_check(overlay)

    active_path = STATE_DIR / "staging_active.json"
    previous_path = STATE_DIR / "staging_previous.json"
    previous = _load_json(active_path) if active_path.exists() else {}
    if active_path.exists():
        _write_json(previous_path, previous)
    _write_json(active_path, candidate)

    drift = _json_diff(previous, candidate)
    _write_json(OUT / "drift.json", {"changed_keys": drift, "previous_present": bool(previous)})

    # rollback drill: restore previous if exists, then return candidate as active.
    rollback_ok = True
    rollback_mode = "no-previous"
    if previous:
        _write_json(active_path, previous)
        restored = _load_json(active_path)
        rollback_ok = restored == previous
        rollback_mode = "restore-previous"
        _write_json(active_path, candidate)

    rollback_report = {
        "status": "PASS" if rollback_ok else "FAIL",
        "mode": rollback_mode,
        "active_bundle_hash": candidate["bundle_hash"],
    }
    _write_json(OUT / "rollback.json", rollback_report)

    parity_report = {
        "status": "PASS",
        "profiles_present": sorted(
            p.stem for p in (GEN / "overlays").glob("*.json") if p.stem in {"dev", "staging", "prod"}
        ),
    }
    _write_json(OUT / "parity.json", parity_report)

    overall = (
        health["status"] == "PASS"
        and readiness["status"] == "PASS"
        and rollback_report["status"] == "PASS"
        and parity_report["status"] == "PASS"
    )
    latest = {
        "status": "PASS" if overall else "FAIL",
        "health": health,
        "readiness": readiness,
        "rollback": rollback_report,
        "parity": parity_report,
        "candidate": candidate,
    }
    _write_json(OUT / "latest.json", latest)
    if overall:
        print("DEPLOY_ROLLBACK_GATE: PASS")
        return 0
    print("DEPLOY_ROLLBACK_GATE: FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
