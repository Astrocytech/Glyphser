#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import re
import sys
from pathlib import Path

REQ_RE = re.compile(r"^([A-Za-z0-9_.-]+)")


def _req_packages(lock: Path) -> set[str]:
    out: set[str] = set()
    for raw in lock.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("--"):
            continue
        m = REQ_RE.match(line)
        if m:
            out.add(m.group(1).lower())
    return out


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
load_policy = importlib.import_module("tooling.security.advanced_policy").load_policy
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def main(argv: list[str] | None = None) -> int:
    _ = argv
    policy = load_policy()
    allowed_external = {x.lower() for x in policy.get("allow_external_packages", []) if isinstance(x, str)}
    internal_prefixes = tuple(x.lower() for x in policy.get("internal_package_prefixes", []) if isinstance(x, str))

    req = ROOT / "requirements.lock"
    findings: list[str] = []
    packages = _req_packages(req)
    internal = sorted(p for p in packages if p.startswith(internal_prefixes))

    for pkg in internal:
        if pkg not in {"glyphser"}:
            findings.append(f"unexpected_internal_package:{pkg}")
    for pkg in sorted(packages):
        if pkg not in allowed_external and pkg not in {"glyphser"}:
            if pkg.startswith("glyphser"):
                findings.append(f"potential_dependency_confusion:{pkg}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"package_count": len(packages), "internal_packages": internal},
        "metadata": {"gate": "dependency_confusion_gate"},
    }
    out = evidence_root() / "security" / "dependency_confusion_gate.json"
    write_json_report(out, report)
    print(f"DEPENDENCY_CONFUSION_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
