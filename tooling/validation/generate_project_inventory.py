#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "evidence" / "gates" / "structure" / "PROJECT_FILE_INVENTORY.md"

EXCLUDE_DIRS = {".git", ".venv", ".pytest_cache", "__pycache__", ".mypy_cache", ".ruff_cache"}


def _walk_tree(base: Path) -> List[Path]:
    entries: List[Path] = []
    for p in sorted(base.iterdir(), key=lambda x: (x.is_file(), x.name.lower())):
        if p.name in EXCLUDE_DIRS:
            continue
        entries.append(p)
    return entries


def _tree_lines(base: Path, prefix: str = "") -> List[str]:
    lines: List[str] = []
    entries = _walk_tree(base)
    total = len(entries)
    for idx, p in enumerate(entries):
        last = idx == total - 1
        branch = "└── " if last else "├── "
        lines.append(prefix + branch + p.name)
        if p.is_dir():
            ext = "    " if last else "│   "
            lines.extend(_tree_lines(p, prefix + ext))
    return lines


def _purpose(rel: str) -> str:
    if rel.startswith("artifacts/generated/stable/codegen/"):
        return "Stable generated codegen index and canonical runtime generated module digests."
    if rel.startswith("artifacts/generated/stable/metadata/"):
        return "Stable generated metadata and manifests for reproducibility checks."
    if rel.startswith("artifacts/generated/stable/deploy/"):
        return "Stable generated deployment outputs and environment/profile manifests."
    if rel.startswith("artifacts/generated/tmp/"):
        return "Transient generated scratch outputs used during validation workflows."
    if rel.startswith("artifacts/inputs/reference_states/"):
        return "Deterministic reference state fixtures used for recovery/deploy tests."
    if rel.startswith("runtime/"):
        return "Runtime source code and importable application modules."
    if rel.startswith("specs/"):
        return "Normative specification, contracts, and layer documentation."
    if rel.startswith("specs/schemas/"):
        return "Machine-readable schema definitions and schema governance."
    if rel.startswith("artifacts/"):
        return "Deterministic inputs, expected outputs, bundles, or generated artifacts."
    if rel.startswith("evidence/"):
        return "Generated verification evidence, reports, and audit outputs."
    if rel.startswith("tooling/"):
        return "Automation, gate, build, release, or developer tooling script."
    if rel.startswith("tests/"):
        return "Automated test coverage across unit/integration/conformance domains."
    if rel.startswith("governance/"):
        return "Governance policy, roadmap, lint, ecosystem, or structural control docs."
    if rel.startswith("product/"):
        return "Product-facing documentation, operations guides, and public artifacts."
    if rel.startswith("distribution/"):
        return "Release, packaging, signing, and distribution-facing assets."
    if rel.startswith(".github/"):
        return "CI/CD workflow automation configuration."
    return "Repository-level configuration or supporting documentation."


def main() -> int:
    files: List[str] = []
    for p in sorted(ROOT.rglob("*")):
        if any(part in EXCLUDE_DIRS for part in p.parts):
            continue
        if p.is_file():
            files.append(p.relative_to(ROOT).as_posix())

    lines: List[str] = []
    lines.append("# Project File Inventory")
    lines.append("")
    lines.append(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    lines.append("")
    lines.append(
        "Scope: Full repository tree excluding transient local cache directories (`.git`, `.venv`, `.pytest_cache`, `__pycache__`, lint/type caches)."
    )
    lines.append("")
    lines.append("## Full Tree Structure")
    lines.append("```text")
    lines.append(".")
    lines.extend(_tree_lines(ROOT))
    lines.append("```")
    lines.append("")
    lines.append("## File Purpose Index")
    lines.append("| File | Purpose |")
    lines.append("|---|---|")
    for rel in files:
        lines.append(f"| `{rel}` | {_purpose(rel)} |")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"PROJECT_FILE_INVENTORY: wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
