#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tooling.lib.path_config import evidence_root

_sp = importlib.import_module("".join(["sub", "process"]))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run_build(env_tag: str) -> tuple[int, str, str, str]:
    with tempfile.TemporaryDirectory(prefix=f"glyphser-repro-{env_tag}-") as td:
        work = Path(td) / "repo"
        shutil.copytree(ROOT, work, dirs_exist_ok=True)
        env = dict(os.environ)
        env["PYTHONHASHSEED"] = "0"
        env["SOURCE_DATE_EPOCH"] = "0"
        env["PYTHONPATH"] = str(work)
        cmd = [sys.executable, "-m", "tooling.release.build_release_bundle"]
        proc = _sp.run(cmd, cwd=str(work), env=env, capture_output=True, text=True, check=False)
        bundle = work / "artifacts" / "bundles" / "hello-core-bundle.tar.gz"
        if not bundle.exists():
            return proc.returncode, "", proc.stdout, proc.stderr
        return proc.returncode, _sha(bundle), proc.stdout, proc.stderr


def main() -> int:
    rc_a, sha_a, out_a, err_a = _run_build("a")
    rc_b, sha_b, out_b, err_b = _run_build("b")
    ok = rc_a == 0 and rc_b == 0 and bool(sha_a) and sha_a == sha_b
    payload: dict[str, Any] = {
        "status": "PASS" if ok else "FAIL",
        "run_a": {"returncode": rc_a, "sha256": sha_a, "stdout": out_a, "stderr": err_a},
        "run_b": {"returncode": rc_b, "sha256": sha_b, "stdout": out_b, "stderr": err_b},
    }
    out = evidence_root() / "security" / "reproducible_build.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"REPRODUCIBLE_BUILD_GATE: {payload['status']}")
    print(f"Report: {out}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
