#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
DOC_ROOTS = [ROOT / "governance" / "security", ROOT / "docs" / "security"]


def _local_target(base: Path, target: str) -> Path | None:
    t = target.strip()
    if not t or t.startswith(("http://", "https://", "mailto:", "#")):
        return None
    path_part = t.split("#", 1)[0].strip()
    if not path_part:
        return None
    return (base / path_part).resolve() if not Path(path_part).is_absolute() else Path(path_part)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    checked_docs = 0
    checked_links = 0

    docs: list[Path] = []
    for root in DOC_ROOTS:
        if root.exists():
            docs.extend(sorted(root.rglob("*.md")))
    for doc in sorted(docs):
        checked_docs += 1
        text = doc.read_text(encoding="utf-8")
        for raw in LINK_RE.findall(text):
            target = _local_target(doc.parent, raw)
            if target is None:
                continue
            checked_links += 1
            if not target.exists():
                rel_doc = str(doc.relative_to(ROOT)).replace("\\", "/")
                findings.append(f"broken_link:{rel_doc}:{raw}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"checked_docs": checked_docs, "checked_links": checked_links},
        "metadata": {"gate": "runbook_index_health_gate"},
    }
    out = evidence_root() / "security" / "runbook_index_health_gate.json"
    write_json_report(out, report)
    print(f"RUNBOOK_INDEX_HEALTH_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
