#!/usr/bin/env python3
from __future__ import annotations

import ast
import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def _is_zero_literal(node: ast.expr | None) -> bool:
    return isinstance(node, ast.Constant) and isinstance(node.value, int) and node.value == 0


class _ReturnCollector(ast.NodeVisitor):
    def __init__(self) -> None:
        self.returns: list[ast.Return] = []
        self._depth = 0

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: N802
        if self._depth > 0:
            return
        self._depth += 1
        self.generic_visit(node)
        self._depth -= 1

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:  # noqa: N802
        if self._depth > 0:
            return
        self._depth += 1
        self.generic_visit(node)
        self._depth -= 1

    def visit_Lambda(self, node: ast.Lambda) -> None:  # noqa: N802
        _ = node
        return

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: N802
        _ = node
        return

    def visit_Return(self, node: ast.Return) -> None:  # noqa: N802
        self.returns.append(node)


def _collect_returns(func: ast.FunctionDef) -> list[ast.Return]:
    collector = _ReturnCollector()
    collector.visit(func)
    return collector.returns


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    checked_files = 0

    for path in sorted((ROOT / "tooling" / "security").glob("*.py")):
        checked_files += 1
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except Exception:
            findings.append(f"parse_error:{path.name}")
            continue
        for node in tree.body:
            if not isinstance(node, ast.FunctionDef) or node.name != "main":
                continue
            returns = _collect_returns(node)
            if not returns:
                continue
            if all(_is_zero_literal(ret.value) for ret in returns):
                findings.append(f"unconditional_return_zero:{path.name}:{returns[0].lineno}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"checked_files": checked_files, "findings": len(findings)},
        "metadata": {"gate": "unconditional_return_zero_gate"},
    }
    out = evidence_root() / "security" / "unconditional_return_zero_gate.json"
    write_json_report(out, report)
    print(f"UNCONDITIONAL_RETURN_ZERO_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
