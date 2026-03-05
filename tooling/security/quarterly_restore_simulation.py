#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib
import json
import os
import random
import sys
from datetime import UTC, datetime
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


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _seed(raw: str) -> int:
    return int(hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16], 16)


def _verify_sig(path: Path) -> bool:
    sig_path = path.with_suffix(path.suffix + ".sig")
    if not sig_path.exists():
        return False
    sig = sig_path.read_text(encoding="utf-8").strip()
    return bool(sig) and verify_file(path, sig, key=current_key(strict=False))


def _candidate_runs() -> list[Path]:
    if not RUNS_ROOT.exists():
        return []
    return [p for p in sorted(RUNS_ROOT.iterdir()) if p.is_dir()]


def _audit_run(run_dir: Path) -> dict[str, Any]:
    findings: list[str] = []
    audited_stages = 0
    for stage in sorted(p for p in run_dir.iterdir() if p.is_dir()):
        sec = stage / "security"
        if not sec.exists():
            continue
        audited_stages += 1
        manifest = sec / "long_term_retention_manifest.json"
        if not manifest.exists():
            findings.append(f"{stage.name}:missing_long_term_retention_manifest")
            continue
        if not _verify_sig(manifest):
            findings.append(f"{stage.name}:invalid_long_term_retention_manifest_signature")
            continue
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        entries = payload.get("entries", []) if isinstance(payload, dict) else []
        if not isinstance(entries, list):
            findings.append(f"{stage.name}:invalid_manifest_entries")
            continue
        for item in entries:
            if not isinstance(item, dict):
                findings.append(f"{stage.name}:invalid_manifest_entry")
                continue
            rel = str(item.get("path", "")).strip()
            expected = str(item.get("sha256", "")).strip().lower()
            if not rel or not expected:
                findings.append(f"{stage.name}:invalid_manifest_entry_fields")
                continue
            target = ROOT / rel
            if not target.exists():
                findings.append(f"{stage.name}:restored_evidence_missing:{rel}")
                continue
            actual = _sha256(target)
            if actual != expected:
                findings.append(f"{stage.name}:restored_evidence_digest_mismatch:{rel}")

    if audited_stages == 0:
        findings.append("no_security_stages")

    return {
        "run_id": run_dir.name,
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "audited_stages": audited_stages,
    }


def main(argv: list[str] | None = None) -> int:
    _ = argv
    now = datetime.now(UTC)
    quarter = ((now.month - 1) // 3) + 1
    quarter_label = f"{now.year}-Q{quarter}"

    findings: list[str] = []
    candidates = _candidate_runs()
    sample_size = int(os.environ.get("GLYPHSER_QUARTERLY_RESTORE_SAMPLE_SIZE", "1") or "1")
    if sample_size <= 0:
        raise ValueError("GLYPHSER_QUARTERLY_RESTORE_SAMPLE_SIZE must be >= 1")
    seed = os.environ.get("GLYPHSER_QUARTERLY_RESTORE_SEED", quarter_label)
    rng = random.Random(_seed(seed))

    if not candidates:
        findings.append("missing_historical_runs")
        sampled: list[Path] = []
    else:
        sampled = rng.sample(candidates, k=min(sample_size, len(candidates)))

    audits = [_audit_run(run_dir) for run_dir in sampled]
    failed = [item["run_id"] for item in audits if item.get("status") != "PASS"]
    if failed:
        findings.append(f"failed_restore_simulations:{','.join(failed)}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "quarter": quarter_label,
            "sample_seed": seed,
            "candidate_run_count": len(candidates),
            "sampled_run_count": len(sampled),
            "sampled_run_ids": [item.name for item in sampled],
        },
        "metadata": {"gate": "quarterly_restore_simulation", "periodic": "quarterly"},
        "audits": audits,
    }
    out = evidence_root() / "security" / "quarterly_restore_simulation.json"
    write_json_report(out, report)
    print(f"QUARTERLY_RESTORE_SIMULATION: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
