#!/usr/bin/env python3
"""
Merge all Markdown files under the ML2ML docs directory into one text file.
Includes all subdirectories.
"""

from __future__ import annotations
import argparse
from pathlib import Path

# Hardcoded target path as requested
DEFAULT_ROOT = "/home/coka/Desktop/INTERVJUI/IZBR/ML2ML/docs/"

def collect_markdown_files(root: Path) -> list[Path]:
    # rglob handles all subdirectories automatically
    return sorted(p for p in root.rglob("*.md") if p.is_file())

def write_merged(markdown_files: list[Path], root: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8") as out:
        for md_file in markdown_files:
            try:
                # Use relative path for the header to keep it clean
                rel_path = md_file.relative_to(root).as_posix()
            except ValueError:
                # Fallback if file is somehow outside the root
                rel_path = md_file.as_posix()
                
            content = md_file.read_text(encoding="utf-8", errors="replace")

            out.write(f"FILE: {rel_path}\n")
            out.write("=" * (6 + len(rel_path)) + "\n")
            out.write(content)
            if not content.endswith("\n"):
                out.write("\n")
            out.write("\n")

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Merge .md files from ML2ML docs into one .txt file."
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=DEFAULT_ROOT,
        help=f"Root directory to scan (default: {DEFAULT_ROOT})",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="merged_docs.txt",
        help="Output .txt file path (default: merged_docs.txt)",
    )

    args = parser.parse_args()
    root = Path(args.root).resolve()
    output = Path(args.output).resolve()

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"ERROR: Directory does not exist: {root}")

    markdown_files = collect_markdown_files(root)
    if not markdown_files:
        raise SystemExit(f"ERROR: No .md files found under: {root}")

    write_merged(markdown_files, root, output)
    print(f"Success! Merged {len(markdown_files)} files from {root}")
    print(f"Output saved to: {output}")

if __name__ == "__main__":
    main()
