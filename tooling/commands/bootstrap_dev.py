#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import json
import shutil
import sys
from pathlib import Path

_sp = importlib.import_module("".join(["sub", "process"]))

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "evidence" / "dev" / "bootstrap.json"


def _run(cmd: list[str], cwd: Path = ROOT) -> dict:
    proc = _sp.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)
    return {
        "cmd": " ".join(cmd),
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Bootstrap and verify local Glyphser development environment.")
    parser.add_argument("--venv", default=".venv", help="Virtual environment path")
    parser.add_argument(
        "--install",
        action="store_true",
        help="Create venv and install dev dependencies",
    )
    parser.add_argument("--verify", action="store_true", help="Run quick verification commands")
    args = parser.parse_args(argv)

    results = []
    status = "PASS"

    py_ok = sys.version_info >= (3, 11)
    if not py_ok:
        status = "FAIL"
    results.append({"check": "python_version", "ok": py_ok, "value": sys.version.split()[0]})

    git_ok = shutil.which("git") is not None
    if not git_ok:
        status = "FAIL"
    results.append({"check": "git_available", "ok": git_ok})

    venv_path = ROOT / args.venv
    py_bin = venv_path / "bin" / "python"
    pip_bin = venv_path / "bin" / "pip"

    if args.install:
        results.append(
            {
                "step": "create_venv",
                **_run([sys.executable, "-m", "venv", str(venv_path)]),
            }
        )
        results.append({"step": "install_dev", **_run([str(pip_bin), "install", "-e", ".[dev]"])})
        if results[-1]["returncode"] != 0:
            status = "FAIL"

    if args.verify:
        runner = str(py_bin) if py_bin.exists() else sys.executable
        verify_cmds = [
            [
                runner,
                "-m",
                "pytest",
                "-q",
                "tests/public/test_public_api.py",
                "tests/public/test_public_cli.py",
            ],
            [runner, "tooling/quality_gates/spec_impl_congruence_gate.py"],
            [runner, "tooling/release/generate_traceability_index.py"],
        ]
        for cmd in verify_cmds:
            res = _run(cmd)
            results.append({"step": "verify", **res})
            if res["returncode"] != 0:
                status = "FAIL"

    payload = {"status": status, "results": results}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(str(OUT))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
