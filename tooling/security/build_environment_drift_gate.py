#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib
import json
import platform
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
load_stage_s_policy = importlib.import_module("tooling.security.stage_s_policy").load_stage_s_policy
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


TICKET_RE = re.compile(r"^(SEC-|ADR-|TICKET-)")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv: list[str] | None = None) -> int:
    _ = argv
    cfg = load_stage_s_policy().get("build_environment", {})
    allow_py = [x for x in cfg.get("allow_python_prefixes", []) if isinstance(x, str)]
    allow_plat = [x for x in cfg.get("allow_platform_prefixes", []) if isinstance(x, str)]
    baseline_path = ROOT / str(cfg.get("baseline_file", "governance/security/build_env_baseline.json"))
    approval_path = ROOT / str(cfg.get("drift_approval_file", "governance/security/build_env_drift_approval.json"))

    py_ver = platform.python_version()
    plat = platform.system()
    lock_sha = _sha(ROOT / "tooling" / "security" / "security_toolchain_lock.json")

    findings: list[str] = []
    if not any(py_ver.startswith(p) for p in allow_py):
        findings.append(f"python_version_not_allowed:{py_ver}")
    if not any(plat.startswith(p) for p in allow_plat):
        findings.append(f"platform_not_allowed:{plat}")

    baseline = json.loads(baseline_path.read_text(encoding="utf-8")) if baseline_path.exists() else {}
    expected = str(baseline.get("toolchain_lock_sha256", "sha256:auto"))
    if expected not in {"", "sha256:auto", lock_sha}:
        approval = json.loads(approval_path.read_text(encoding="utf-8")) if approval_path.exists() else {}
        ticket = str(approval.get("ticket", ""))
        if not TICKET_RE.match(ticket):
            findings.append("toolchain_lock_drift_without_approval")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"python_version": py_ver, "platform": plat, "toolchain_lock_sha256": lock_sha},
        "metadata": {"gate": "build_environment_drift_gate"},
    }
    out = evidence_root() / "security" / "build_environment_drift_gate.json"
    write_json_report(out, report)
    print(f"BUILD_ENVIRONMENT_DRIFT_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
