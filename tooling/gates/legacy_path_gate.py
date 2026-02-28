#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "evidence" / "structure"

TARGET_DIRS = ["src", "tooling", "tests", ".github"]
EXTS = {".py", ".yml", ".yaml", ".toml", ".md", ".json"}

LEGACY_PATTERNS = [
    re.compile(r'ROOT\s*/\s*"fixtures"'),
    re.compile(r"ROOT\s*/\s*'fixtures'"),
    re.compile(r'ROOT\s*/\s*"vectors"'),
    re.compile(r"ROOT\s*/\s*'vectors'"),
    re.compile(r'ROOT\s*/\s*"goldens"'),
    re.compile(r"ROOT\s*/\s*'goldens'"),
    re.compile(r'ROOT\s*/\s*"generated"'),
    re.compile(r"ROOT\s*/\s*'generated'"),
    re.compile(r'ROOT\s*/\s*"dist"'),
    re.compile(r"ROOT\s*/\s*'dist'"),
    re.compile(r'ROOT\s*/\s*"reports"'),
    re.compile(r"ROOT\s*/\s*'reports'"),
    re.compile(r'"fixtures/'),
    re.compile(r"'fixtures/"),
    re.compile(r'"vectors/'),
    re.compile(r"'vectors/"),
    re.compile(r'"goldens/'),
    re.compile(r"'goldens/"),
    re.compile(r'"generated/'),
    re.compile(r"'generated/"),
    re.compile(r'"dist/'),
    re.compile(r"'dist/"),
    re.compile(r'"reports/'),
    re.compile(r"'reports/"),
    re.compile(r'conformance/reports/'),
    re.compile(r'conformance/results/'),
]

ALLOW_SUBSTRINGS = [
    "artifacts/inputs/fixtures/",
    "artifacts/inputs/vectors/",
    "artifacts/expected/goldens/",
    "artifacts/generated/",
    "artifacts/bundles/",
    "evidence/",
    "evidence/conformance/reports/",
    "evidence/conformance/results/",
]


def _scan_file(path: Path) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    for i, line in enumerate(lines, start=1):
        for pat in LEGACY_PATTERNS:
            if not pat.search(line):
                continue
            if any(ok in line for ok in ALLOW_SUBSTRINGS):
                continue
            findings.append(
                {
                    "file": str(path.relative_to(ROOT)).replace("\\", "/"),
                    "line": i,
                    "pattern": pat.pattern,
                    "text": line.strip()[:200],
                }
            )
    return findings


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    findings: list[dict[str, object]] = []
    for rel in TARGET_DIRS:
        base = ROOT / rel
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            if path.name == "legacy_path_gate.py":
                continue
            if path.suffix and path.suffix.lower() not in EXTS:
                continue
            findings.extend(_scan_file(path))

    status = "PASS" if not findings else "FAIL"
    report = {"status": status, "findings": findings}
    (OUT / "legacy_path_gate.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if status == "PASS":
        print("LEGACY_PATH_GATE: PASS")
        return 0
    print("LEGACY_PATH_GATE: FAIL")
    for f in findings[:20]:
        print(f" - {f['file']}:{f['line']} matches {f['pattern']}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
