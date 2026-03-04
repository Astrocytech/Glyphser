#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root

EXCLUDED = {
    "__init__.py",
    "security_super_gate.py",
}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec_dir = ROOT / "tooling" / "security"
    wf_dir = ROOT / ".github" / "workflows"

    gates = sorted(p.name for p in sec_dir.glob("*_gate.py") if p.name not in EXCLUDED)
    super_gate_text = (sec_dir / "security_super_gate.py").read_text(encoding="utf-8")
    workflow_text = "\n".join(p.read_text(encoding="utf-8") for p in sorted(wf_dir.glob("*.yml")))

    findings: list[str] = []
    dead: list[str] = []
    for gate in gates:
        if gate not in super_gate_text and gate not in workflow_text:
            dead.append(gate)
            findings.append(f"dead_gate_not_wired:{gate}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"total_gates": len(gates), "dead_gates": len(dead)},
        "metadata": {"gate": "security_dead_gate_wiring_gate"},
        "dead_gates": dead,
    }
    out = evidence_root() / "security" / "security_dead_gate_wiring_gate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"SECURITY_DEAD_GATE_WIRING_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
