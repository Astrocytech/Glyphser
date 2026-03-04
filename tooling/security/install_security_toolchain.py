#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

run_checked = importlib.import_module("tooling.security.subprocess_policy").run_checked

ROOT = Path(__file__).resolve().parents[2]
LOCK_PATH = ROOT / "tooling" / "security" / "security_toolchain_lock.json"
CONSTRAINTS_PATH = ROOT / "tooling" / "security" / "security_toolchain_constraints.txt"


def _load_lock_versions() -> dict[str, str]:
    payload = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("invalid security toolchain lock")
    out: dict[str, str] = {}
    for name, spec in payload.items():
        if not isinstance(name, str) or not isinstance(spec, dict):
            continue
        version = str(spec.get("version", "")).strip()
        if version:
            out[name] = version
    return out


def _load_constraints_versions() -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in CONSTRAINTS_PATH.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "==" not in line:
            raise ValueError(f"invalid constraints line: {line}")
        name, version = line.split("==", 1)
        out[name.strip()] = version.strip()
    return out


def main(argv: list[str] | None = None) -> int:
    _ = argv
    lock_versions = _load_lock_versions()
    constraints_versions = _load_constraints_versions()
    if lock_versions != constraints_versions:
        missing_in_constraints = sorted(set(lock_versions) - set(constraints_versions))
        missing_in_lock = sorted(set(constraints_versions) - set(lock_versions))
        mismatched = sorted(
            name
            for name in set(lock_versions).intersection(constraints_versions)
            if lock_versions[name] != constraints_versions[name]
        )
        detail = {
            "missing_in_constraints": missing_in_constraints,
            "missing_in_lock": missing_in_lock,
            "version_mismatch": mismatched,
        }
        raise ValueError(f"security toolchain constraints mismatch lock: {detail}")

    cmds = [
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
        [sys.executable, "-m", "pip", "install", "--upgrade", "-r", str(CONSTRAINTS_PATH)],
    ]
    for cmd in cmds:
        proc = run_checked(cmd)
        if proc.returncode != 0:
            print(proc.stdout, end="")
            print(proc.stderr, end="", file=sys.stderr)
            return int(proc.returncode)
    print("SECURITY_TOOLCHAIN_INSTALL: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
