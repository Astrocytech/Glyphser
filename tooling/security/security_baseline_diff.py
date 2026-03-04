#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
current_key = artifact_signing.current_key
sign_file = artifact_signing.sign_file
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
run_checked = importlib.import_module("tooling.security.subprocess_policy").run_checked


def main(argv: list[str] | None = None) -> int:
    _ = argv
    baseline_files = [
        "tooling/security/security_toolchain_lock.json",
        "tooling/security/semgrep-rules.yml",
        "tooling/security/bandit.yaml",
    ]
    proc = run_checked(["git", "diff", "--", *baseline_files], cwd=ROOT)
    diff_text = proc.stdout
    sec = evidence_root() / "security"
    sec.mkdir(parents=True, exist_ok=True)
    diff_path = sec / "security_baseline_diff.txt"
    diff_path.write_text(diff_text, encoding="utf-8")
    sig_path = sec / "security_baseline_diff.txt.sig"
    sig_path.write_text(sign_file(diff_path, key=current_key(strict=False)) + "\n", encoding="utf-8")
    report = {
        "status": "PASS",
        "findings": [],
        "summary": {"changed": bool(diff_text.strip()), "baseline_files": baseline_files},
        "metadata": {"gate": "security_baseline_diff"},
    }
    out = sec / "security_baseline_diff.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"SECURITY_BASELINE_DIFF: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
