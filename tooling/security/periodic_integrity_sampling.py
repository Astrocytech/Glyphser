#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib
import json
import os
import random
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
current_key = artifact_signing.current_key
verify_file = artifact_signing.verify_file
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

RUNS_ROOT = ROOT / "evidence" / "runs"
REQUIRED_REPORTS = ("security_super_gate.json", "evidence_attestation_index.json", "rolling_merkle_checkpoints.json")


def _seed_value(raw: str) -> int:
    return int(hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16], 16)


def _candidate_run_dirs() -> list[Path]:
    if not RUNS_ROOT.exists():
        return []
    out: list[Path] = []
    for run_dir in sorted(p for p in RUNS_ROOT.iterdir() if p.is_dir()):
        if any((stage / "security").is_dir() for stage in run_dir.iterdir() if stage.is_dir()):
            out.append(run_dir)
    return out


def _verify_signature(path: Path) -> bool:
    sig_path = path.with_suffix(path.suffix + ".sig")
    if not sig_path.exists():
        return False
    signature = sig_path.read_text(encoding="utf-8").strip()
    return verify_file(path, signature, key=current_key(strict=False))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _retention_spotcheck(sec: Path) -> tuple[list[str], dict[str, Any]]:
    findings: list[str] = []
    manifest_path = sec / "long_term_retention_manifest.json"
    if not manifest_path.exists():
        findings.append("missing_long_term_retention_manifest")
        return findings, {"manifest_present": False, "entries_checked": 0}
    if not _verify_signature(manifest_path):
        findings.append("invalid_long_term_retention_manifest_signature")
        return findings, {"manifest_present": True, "signature_ok": False, "entries_checked": 0}
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = payload.get("entries", []) if isinstance(payload, dict) else []
    if not isinstance(entries, list):
        entries = []
        findings.append("invalid_long_term_retention_manifest_entries")
    checked = 0
    mismatches = 0
    for item in entries:
        if not isinstance(item, dict):
            findings.append("invalid_manifest_entry")
            continue
        rel = str(item.get("path", "")).strip()
        expected = str(item.get("sha256", "")).strip().lower()
        if not rel or not expected:
            findings.append("invalid_manifest_entry_fields")
            continue
        target = ROOT / rel
        checked += 1
        if not target.exists():
            mismatches += 1
            findings.append(f"restored_evidence_missing:{rel}")
            continue
        actual = _sha256(target)
        if actual != expected:
            mismatches += 1
            findings.append(f"restored_evidence_digest_mismatch:{rel}")
    return findings, {"manifest_present": True, "signature_ok": True, "entries_checked": checked, "mismatches": mismatches}


def _audit_run(run_dir: Path) -> dict[str, Any]:
    stages = sorted(p for p in run_dir.iterdir() if p.is_dir())
    stage_results: list[dict[str, Any]] = []
    run_findings: list[str] = []

    for stage in stages:
        sec = stage / "security"
        if not sec.exists():
            continue
        missing = [name for name in REQUIRED_REPORTS if not (sec / name).exists()]
        signatures = {
            "evidence_attestation_index": _verify_signature(sec / "evidence_attestation_index.json")
            if (sec / "evidence_attestation_index.json").exists()
            else False,
            "rolling_merkle_checkpoints": _verify_signature(sec / "rolling_merkle_checkpoints.json")
            if (sec / "rolling_merkle_checkpoints.json").exists()
            else False,
        }
        if missing:
            run_findings.append(f"{stage.name}:missing_reports:{','.join(missing)}")
        for report_name, ok in signatures.items():
            if not ok:
                run_findings.append(f"{stage.name}:signature_verify_failed:{report_name}")

        retention_findings, retention_summary = _retention_spotcheck(sec)
        for finding in retention_findings:
            run_findings.append(f"{stage.name}:{finding}")

        stage_results.append(
            {
                "stage": stage.name,
                "missing_reports": missing,
                "signature_checks": signatures,
                "retention_spotcheck": retention_summary,
            }
        )

    if not stage_results:
        run_findings.append("no_security_stage_data")

    return {
        "run_id": run_dir.name,
        "status": "PASS" if not run_findings else "FAIL",
        "findings": run_findings,
        "stages": stage_results,
    }


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    sec.mkdir(parents=True, exist_ok=True)

    findings: list[str] = []
    candidates = _candidate_run_dirs()
    sample_size = int(os.environ.get("GLYPHSER_INTEGRITY_SAMPLE_SIZE", "3"))
    if sample_size <= 0:
        raise ValueError("GLYPHSER_INTEGRITY_SAMPLE_SIZE must be >= 1")

    seed_input = os.environ.get("GLYPHSER_INTEGRITY_SAMPLE_SEED", "weekly-security-maintenance")
    rng = random.Random(_seed_value(seed_input))

    if not candidates:
        findings.append("missing_historical_runs")
        sampled: list[Path] = []
    else:
        sampled = rng.sample(candidates, k=min(sample_size, len(candidates)))

    audits = [_audit_run(run_dir) for run_dir in sampled]
    failed_runs = sorted(item["run_id"] for item in audits if item["status"] != "PASS")
    if failed_runs:
        findings.append(f"failed_sampled_runs:{','.join(failed_runs)}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "sample_seed": seed_input,
            "candidate_run_count": len(candidates),
            "sampled_run_count": len(sampled),
            "sampled_run_ids": [path.name for path in sampled],
        },
        "metadata": {"gate": "periodic_integrity_sampling", "periodic": True, "random_audit_selection": True},
        "audits": audits,
    }
    out = sec / "periodic_integrity_sampling.json"
    write_json_report(out, report)
    print(f"PERIODIC_INTEGRITY_SAMPLING: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
