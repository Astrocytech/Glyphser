#!/usr/bin/env python3
"""Generate API reference docs for the stable Glyphser public API."""

from __future__ import annotations

import inspect
import sys
from dataclasses import is_dataclass
from pathlib import Path
from typing import Any

from glyphser import RuntimeApiConfig, RuntimeService, VerificationResult, verify

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "API_REFERENCE.md"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _format_signature(obj: Any) -> str:
    try:
        return str(inspect.signature(obj))
    except (TypeError, ValueError):
        return "(...)"


def _doc(obj: Any) -> str:
    text = inspect.getdoc(obj) or "No description provided."
    return text.strip()


def build_markdown() -> str:
    lines: list[str] = []
    lines.append("# API Reference")
    lines.append("")
    lines.append("This file is auto-generated from the stable `glyphser.public` API.")
    lines.append("")
    lines.append("Regenerate with:")
    lines.append("```bash")
    lines.append("python tooling/docs/generate_api_reference.py")
    lines.append("```")
    lines.append("")

    symbols = [
        ("verify", verify),
        ("VerificationResult", VerificationResult),
        ("RuntimeApiConfig", RuntimeApiConfig),
        ("RuntimeService", RuntimeService),
    ]

    for name, obj in symbols:
        lines.append(f"## `{name}`")
        lines.append("")
        if inspect.isclass(obj):
            kind = "dataclass" if is_dataclass(obj) else "class"
            lines.append(f"Type: `{kind}`")
            lines.append("")
            lines.append(f"Signature: `{name}{_format_signature(obj)}`")
            lines.append("")
            lines.append(_doc(obj))
            lines.append("")
        else:
            lines.append("Type: `function`")
            lines.append("")
            lines.append(f"Signature: `{name}{_format_signature(obj)}`")
            lines.append("")
            lines.append(_doc(obj))
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    OUT.write_text(build_markdown(), encoding="utf-8")
    print(str(OUT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
