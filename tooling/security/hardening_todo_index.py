#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

SECTION_RE = re.compile(r"^([A-Z0-9]{1,4})\.\s+")
INDEX_BEGIN = "<HARDENING_INDEX_BEGIN>"
INDEX_END = "<HARDENING_INDEX_END>"
DEFAULT_TODO = (
    "/home/coka/Desktop/ASTROCYTECH/ASTROCYTECH_DIARY/TODOs/"
    "glyphser_security_hardening_master_todo.txt"
)


def _collect_counts(lines: list[str]) -> dict[str, dict[str, int]]:
    current = "GLOBAL"
    counts: dict[str, dict[str, int]] = {current: {"pending": 0, "in_progress": 0, "done": 0}}
    for line in lines:
        match = SECTION_RE.match(line.strip())
        if match:
            current = match.group(1)
            counts.setdefault(current, {"pending": 0, "in_progress": 0, "done": 0})
            continue
        stripped = line.strip()
        if stripped.startswith("[ ]"):
            counts[current]["pending"] += 1
        elif stripped.startswith("[~]"):
            counts[current]["in_progress"] += 1
        elif stripped.startswith("[x]"):
            counts[current]["done"] += 1
    return counts


def _build_index(counts: dict[str, dict[str, int]]) -> list[str]:
    rows = [
        INDEX_BEGIN,
        "Hardening Index",
        "Format: SECTION pending/in_progress/done",
    ]
    for section in sorted(counts.keys()):
        c = counts[section]
        rows.append(f"{section} {c['pending']}/{c['in_progress']}/{c['done']}")
    rows.append(INDEX_END)
    return rows


def _replace_or_prepend(content: str, index_lines: list[str]) -> str:
    lines = content.splitlines()
    begin = next((i for i, line in enumerate(lines) if line.strip() == INDEX_BEGIN), None)
    end = next((i for i, line in enumerate(lines) if line.strip() == INDEX_END), None)
    index_block = "\n".join(index_lines)
    if begin is not None and end is not None and begin <= end:
        new_lines = lines[:begin] + [index_block] + lines[end + 1 :]
        return "\n".join(new_lines).rstrip() + "\n"
    return index_block + "\n\n" + content.lstrip("\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Update hardening TODO index block with per-section counts.")
    parser.add_argument("--todo", default=DEFAULT_TODO, help="Path to hardening TODO text file.")
    args = parser.parse_args([] if argv is None else argv)

    path = Path(args.todo).expanduser()
    if not path.exists():
        print(f"HARDENING_TODO_INDEX: SKIP (missing file: {path})")
        return 0
    content = path.read_text(encoding="utf-8")
    counts = _collect_counts(content.splitlines())
    updated = _replace_or_prepend(content, _build_index(counts))
    path.write_text(updated, encoding="utf-8")
    print(f"HARDENING_TODO_INDEX: UPDATED {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
