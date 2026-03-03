#!/usr/bin/env python3
from __future__ import annotations

import fnmatch
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tooling.quality_gates.telemetry import emit_gate_trace

POLICY = ROOT / "governance" / "structure" / "evidence_storage_policy.json"
OUT = ROOT / "evidence" / "gates" / "quality" / "evidence_storage_policy.json"


def _tracked_paths(root: Path) -> list[str]:
    proc = subprocess.run(["git", "ls-files"], cwd=root, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def evaluate(root: Path = ROOT, tracked_paths: list[str] | None = None) -> dict:
    findings: list[str] = []
    if not POLICY.exists():
        findings.append("missing_policy_file")
        payload = {"status": "FAIL", "findings": findings}
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        emit_gate_trace(root, "evidence_storage_policy", payload)
        return payload

    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    mode = policy.get("mode", "")
    forbidden_globs = [str(x) for x in policy.get("forbidden_globs", [])]
    required_paths = [str(x) for x in policy.get("required_paths", [])]

    if mode != "versioned_audit":
        findings.append(f"unsupported_mode:{mode}")

    tracked = tracked_paths if tracked_paths is not None else _tracked_paths(root)

    for req in required_paths:
        if req not in tracked:
            findings.append(f"missing_required_tracked_path:{req}")

    for p in tracked:
        for pat in forbidden_globs:
            if fnmatch.fnmatch(p, pat):
                findings.append(f"forbidden_tracked_path:{p}")

    gitignore = (root / ".gitignore").read_text(encoding="utf-8", errors="ignore") if (root / ".gitignore").exists() else ""
    for pat in forbidden_globs:
        if pat not in gitignore:
            findings.append(f"missing_gitignore_pattern:{pat}")

    payload = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "mode": mode,
        "required_paths_checked": len(required_paths),
        "tracked_file_count": len(tracked),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    emit_gate_trace(root, "evidence_storage_policy", payload)
    return payload


def main() -> int:
    report = evaluate(ROOT)
    if report["status"] == "PASS":
        print("EVIDENCE_STORAGE_POLICY_GATE: PASS")
        return 0
    print("EVIDENCE_STORAGE_POLICY_GATE: FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
