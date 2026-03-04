#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "evidence" / "gates" / "structure"

DOC_EXTS = {".md", ".txt", ".rst"}
CODE_EXTS = {
    ".py",
    ".sh",
    ".bash",
    ".zsh",
    ".js",
    ".ts",
    ".go",
    ".rs",
    ".java",
    ".c",
    ".cc",
    ".cpp",
}
CODE_DIRS = (
    "runtime",
    "tooling/codegen",
    "tooling/conformance",
    "tooling/deploy",
    "tooling/scripts",
    "tests",
    "artifacts/generated",
)
DOC_DIRS = ("docs", "specs", "governance", "product")
ALLOWED_ROOT_DOCS = {
    "README.md",
    "CHANGELOG.md",
    "ROADMAP.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "SECURITY.md",
    "VERSIONING.md",
    "REDUCE_TO_VANILLA.md",
    "RELEASE_NOTES_v0.1.0.md",
}
ALLOWED_DOCS_IN_CODE_DIRS = {
    "tooling/scripts/repro/java_bridge/README_M13_JAVA_RUNTIME_HARDENING.md",
    "tooling/scripts/repro/rust_bridge/README_M14_RUST_BRIDGE.md",
}


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def evaluate() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    doc_in_code: list[str] = []
    code_in_docs: list[str] = []
    unexpected_root_docs: list[str] = []

    for code_dir in CODE_DIRS:
        for p in (ROOT / code_dir).rglob("*"):
            if p.is_file() and p.suffix.lower() in DOC_EXTS:
                relp = _rel(p)
                if relp not in ALLOWED_DOCS_IN_CODE_DIRS:
                    doc_in_code.append(relp)

    for doc_dir in DOC_DIRS:
        for p in (ROOT / doc_dir).rglob("*"):
            if p.is_file() and p.suffix.lower() in CODE_EXTS:
                code_in_docs.append(_rel(p))

    for p in ROOT.iterdir():
        if not p.is_file():
            continue
        if p.suffix.lower() in DOC_EXTS and p.name not in ALLOWED_ROOT_DOCS:
            unexpected_root_docs.append(p.name)

    latest = {
        "status": "PASS" if not doc_in_code and not code_in_docs and not unexpected_root_docs else "FAIL",
        "doc_files_in_code_dirs": sorted(doc_in_code),
        "code_files_in_doc_dirs": sorted(code_in_docs),
        "unexpected_root_doc_files": sorted(unexpected_root_docs),
    }
    (OUT / "latest.json").write_text(json.dumps(latest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return latest


def main() -> int:
    report = evaluate()
    if report["status"] == "PASS":
        print("DOC_CODE_SEPARATION_GATE: PASS")
        return 0
    print("DOC_CODE_SEPARATION_GATE: FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
