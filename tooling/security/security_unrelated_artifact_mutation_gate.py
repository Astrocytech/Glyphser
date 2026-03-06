#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tooling.lib.path_config import evidence_root
from tooling.security.report_io import write_json_report
from tooling.security.subprocess_policy import run_checked

POLICY = ROOT / "governance" / "security" / "security_unrelated_artifact_mutation_policy.json"
DEFAULT_ALLOWED_MUTATION_PREFIXES = ["evidence/security/"]
DEFAULT_PROBE_COMMANDS = [["python", "tooling/security/security_primary_report_path_gate.py"]]
DEFAULT_TIMEOUT_SEC = 300.0


def _load_policy(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("unrelated artifact mutation policy must be an object")
    return payload


def _normalize_prefixes(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    out: list[str] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, str):
            continue
        token = item.strip()
        if not token:
            continue
        if not token.endswith("/"):
            token = token + "/"
        if token in seen:
            continue
        seen.add(token)
        out.append(token)
    return out


def _normalize_probe_commands(value: Any) -> list[list[str]]:
    if not isinstance(value, list):
        return []
    out: list[list[str]] = []
    for item in value:
        if not isinstance(item, list):
            continue
        cmd = [str(part).strip() for part in item if str(part).strip()]
        if cmd:
            out.append(cmd)
    return out


def _tracked_paths(root: Path) -> list[str]:
    proc = subprocess.run(
        ["git", "ls-files"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if proc.returncode != 0:
        return []
    return sorted(line.strip() for line in proc.stdout.splitlines() if line.strip())


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _snapshot_hashes(root: Path, relpaths: list[str]) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for rel in relpaths:
        path = root / rel
        if path.exists() and path.is_file():
            hashes[rel] = _hash_file(path)
    return hashes


def _allowed(relpath: str, prefixes: list[str]) -> bool:
    return any(relpath.startswith(prefix) for prefix in prefixes)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not POLICY.exists():
        findings.append("missing_unrelated_artifact_mutation_policy")
        policy: dict[str, Any] = {}
    else:
        try:
            policy = _load_policy(POLICY)
        except Exception:
            findings.append("invalid_unrelated_artifact_mutation_policy")
            policy = {}

    allowed_prefixes = _normalize_prefixes(policy.get("allowed_mutation_prefixes")) or DEFAULT_ALLOWED_MUTATION_PREFIXES
    probe_commands = _normalize_probe_commands(policy.get("probe_commands")) or DEFAULT_PROBE_COMMANDS
    timeout = float(policy.get("max_probe_runtime_sec", DEFAULT_TIMEOUT_SEC))
    if timeout <= 0:
        timeout = DEFAULT_TIMEOUT_SEC

    relpaths = _tracked_paths(ROOT)
    if not relpaths:
        findings.append("unable_to_enumerate_tracked_paths")

    before = _snapshot_hashes(ROOT, relpaths)

    for cmd in probe_commands:
        for _ in range(2):
            proc = run_checked(cmd, cwd=ROOT, timeout_sec=timeout, max_output_bytes=2_000_000)
            if proc.returncode != 0:
                findings.append(f"probe_command_failed:{' '.join(cmd)}")
                break

    after = _snapshot_hashes(ROOT, relpaths)
    changed = sorted(rel for rel in set(before) | set(after) if before.get(rel) != after.get(rel))
    unexpected = sorted(rel for rel in changed if not _allowed(rel, allowed_prefixes))
    findings.extend(f"unexpected_artifact_mutation:{rel}" for rel in unexpected)

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "tracked_paths": len(relpaths),
            "probe_command_count": len(probe_commands),
            "changed_paths": len(changed),
            "unexpected_mutations": len(unexpected),
        },
        "metadata": {"gate": "security_unrelated_artifact_mutation_gate"},
    }
    out = evidence_root() / "security" / "security_unrelated_artifact_mutation_gate.json"
    write_json_report(out, report)
    print(f"SECURITY_UNRELATED_ARTIFACT_MUTATION_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
