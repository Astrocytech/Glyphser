#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "evidence" / "gates" / "structure" / "domain_dependency_gate.json"

IMPORT_PAT = re.compile(r"^\s*(?:from|import)\s+([a-zA-Z0-9_\.]+)")


def _scan_python(base: Path) -> List[Path]:
    if not base.exists():
        return []
    return sorted(p for p in base.rglob("*.py") if p.is_file())


def _violations_for_runtime() -> List[Dict[str, object]]:
    forbidden_import_roots = {
        "tooling",
        "artifacts",
        "evidence",
        "governance",
        "product",
        "specs",
        "tests",
    }
    forbidden_path_tokens = (
        "/tooling/",
        "/artifacts/",
        "/evidence/",
        "/governance/",
        "/product/",
        "/specs/",
    )
    violations: List[Dict[str, object]] = []
    for path in _scan_python(ROOT / "runtime"):
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        for i, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
            m = IMPORT_PAT.search(line)
            if m:
                root = m.group(1).split(".", 1)[0]
                if root in forbidden_import_roots:
                    violations.append(
                        {
                            "file": rel,
                            "line": i,
                            "kind": "import",
                            "text": line.strip()[:200],
                        }
                    )
            normalized = line.replace("\\", "/")
            if any(token in normalized for token in forbidden_path_tokens):
                violations.append(
                    {
                        "file": rel,
                        "line": i,
                        "kind": "path_ref",
                        "text": line.strip()[:200],
                    }
                )
    return violations


def _violations_for_tooling() -> List[Dict[str, object]]:
    forbidden_import_roots = {"product", "governance", "evidence", "specs"}
    violations: List[Dict[str, object]] = []
    for path in _scan_python(ROOT / "tooling"):
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        for i, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
            m = IMPORT_PAT.search(line)
            if not m:
                continue
            root = m.group(1).split(".", 1)[0]
            if root in forbidden_import_roots:
                violations.append(
                    {
                        "file": rel,
                        "line": i,
                        "kind": "import",
                        "text": line.strip()[:200],
                    }
                )
    return violations


def evaluate() -> Dict[str, object]:
    runtime_violations = _violations_for_runtime()
    tooling_violations = _violations_for_tooling()
    payload: Dict[str, object] = {
        "status": "PASS" if not runtime_violations and not tooling_violations else "FAIL",
        "checks": [
            {
                "name": "runtime_domain_dependencies",
                "status": "PASS" if not runtime_violations else "FAIL",
                "violations": runtime_violations,
            },
            {
                "name": "tooling_domain_dependencies",
                "status": "PASS" if not tooling_violations else "FAIL",
                "violations": tooling_violations,
            },
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    report = evaluate()
    if report["status"] == "PASS":
        print("DOMAIN_DEPENDENCY_GATE: PASS")
        return 0
    print("DOMAIN_DEPENDENCY_GATE: FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
