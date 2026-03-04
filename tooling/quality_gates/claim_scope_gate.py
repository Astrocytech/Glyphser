#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

SCOPE_TOKENS = ("available_local", "available_local_partial", "strict_universal")


def _load_text(paths: list[Path]) -> str:
    chunks: list[str] = []
    for path in paths:
        if path.exists():
            chunks.append(path.read_text(encoding="utf-8", errors="ignore"))
    return "\n".join(chunks)


def main() -> int:
    parser = argparse.ArgumentParser(description="Enforce scoped universality claim language.")
    parser.add_argument("--report", required=True, help="Output report json path.")
    parser.add_argument(
        "--check-path",
        action="append",
        default=[],
        help="Files to scan for unscoped 'universal' claims (optional; defaults to known-limitations in report dir).",
    )
    args = parser.parse_args()

    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    check_paths = (
        [Path(p) for p in args.check_path] if args.check_path else [report_path.parent / "known-limitations.md"]
    )

    text = _load_text(check_paths).lower()
    has_universal = "universal" in text
    has_scoped = any(tok in text for tok in SCOPE_TOKENS)

    if has_universal and not has_scoped:
        payload = {
            "status": "FAIL",
            "reason": "Found unscoped universality language.",
            "checked_paths": [str(p) for p in check_paths],
            "scope_tokens": list(SCOPE_TOKENS),
        }
        report_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 1

    payload = {
        "status": "PASS",
        "reason": "Scope-qualified universality language check passed.",
        "checked_paths": [str(p) for p in check_paths],
        "scope_tokens": list(SCOPE_TOKENS),
    }
    report_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
