#!/usr/bin/env python3
from __future__ import annotations

import importlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

RULES_FILE = ROOT / "tooling" / "security" / "semgrep-rules.yml"
RULE_ID_RE = re.compile(r"^\s*-\s+id:\s*([A-Za-z0-9._-]+)\s*$")
EXPECTED_RULE_IDS = {
    "glyphser.subprocess-shell-true",
    "glyphser.dynamic-code-execution",
    "glyphser.unsafe-yaml-load",
    "glyphser.path-traversal-archive-extractall",
    "glyphser.unsafe-tempfile-mktemp",
    "glyphser.unsafe-tempfile-delete-false",
    "glyphser.path-join-untrusted",
    "glyphser.permissive-file-mode",
}


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    if not RULES_FILE.exists():
        findings.append("missing_rules_file:tooling/security/semgrep-rules.yml")
        ids: set[str] = set()
    else:
        ids = set()
        for idx, line in enumerate(RULES_FILE.read_text(encoding="utf-8").splitlines(), start=1):
            m = RULE_ID_RE.match(line)
            if m:
                rid = m.group(1)
                if rid in ids:
                    findings.append(f"duplicate_rule_id:{rid}:line:{idx}")
                ids.add(rid)
        missing = sorted(EXPECTED_RULE_IDS - ids)
        for rid in missing:
            findings.append(f"missing_expected_rule_id:{rid}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "rules_file": str(RULES_FILE.relative_to(ROOT)).replace("\\", "/"),
            "parsed_rule_ids": len(ids),
            "expected_rule_ids": len(EXPECTED_RULE_IDS),
        },
        "metadata": {"gate": "semgrep_rules_self_check_gate"},
    }
    out = evidence_root() / "security" / "semgrep_rules_self_check_gate.json"
    write_json_report(out, report)
    print(f"SEMGREP_RULES_SELF_CHECK_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
