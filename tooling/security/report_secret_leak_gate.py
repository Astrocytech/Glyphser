#!/usr/bin/env python3
from __future__ import annotations

import importlib
import os
import json
import re
import sys
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"(?i)secret[_-]?key\s*[:=]\s*['\"][^'\"]{8,}"),
    re.compile(r"(?i)password\s*[:=]\s*['\"][^'\"]{4,}"),
    re.compile(r'"(?i:password)"\s*:\s*"[^"]{4,}"'),
    re.compile(r"-----BEGIN (?:RSA|EC|OPENSSH) PRIVATE KEY-----"),
]

SECRET_INVENTORY = ROOT / "governance" / "security" / "secret_origin_inventory.json"
SENSITIVE_ENV_NAME = re.compile(r"(?:KEY|TOKEN|SECRET|PASSWORD|PRIVATE|HMAC)", re.IGNORECASE)


def _contains_secret(text: str) -> bool:
    for pat in PATTERNS:
        if pat.search(text):
            return True
    return False


def _inventory_secret_names() -> set[str]:
    if not SECRET_INVENTORY.exists():
        return set()
    try:
        payload = json.loads(SECRET_INVENTORY.read_text(encoding="utf-8"))
    except Exception:
        return set()
    secrets = payload.get("secrets", []) if isinstance(payload, dict) else []
    if not isinstance(secrets, list):
        return set()
    names: set[str] = set()
    for item in secrets:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        if name:
            names.add(name)
    return names


def _sensitive_env_entries() -> dict[str, str]:
    pairs: dict[str, str] = {}
    for name, value in os.environ.items():
        if not value:
            continue
        if not SENSITIVE_ENV_NAME.search(name):
            continue
        if len(value) < 6:
            continue
        pairs[name] = value
    for name in _inventory_secret_names():
        value = os.environ.get(name, "")
        if len(value) >= 6:
            pairs[name] = value
    return pairs


def _fingerprint(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()[:12]


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    findings: list[str] = []
    scanned = 0
    env_entries = _sensitive_env_entries()
    env_names = sorted(env_entries.keys(), key=len, reverse=True)
    env_values = sorted(set(env_entries.values()), key=len, reverse=True)
    env_name_echoes = 0
    env_value_echoes = 0
    for path in sorted(sec.glob("*.json")):
        if path.name == "report_secret_leak.json":
            continue
        scanned += 1
        text = path.read_text(encoding="utf-8", errors="ignore")
        if _contains_secret(text):
            findings.append(str(path.relative_to(ROOT)).replace("\\", "/"))
            continue
        try:
            payload = json.loads(text)
        except Exception:
            continue
        report_findings = payload.get("findings", []) if isinstance(payload, dict) else []
        if not isinstance(report_findings, list):
            continue
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        for idx, item in enumerate(report_findings):
            entry = str(item)
            matched_name = next((name for name in env_names if name and name in entry), None)
            if matched_name:
                env_name_echoes += 1
                findings.append(
                    f"secret_env_name_echo:{rel}:finding[{idx}]:name_fp={_fingerprint(matched_name)}"
                )
                break
            matched_value = next((value for value in env_values if value and value in entry), None)
            if matched_value:
                env_value_echoes += 1
                findings.append(
                    f"secret_env_value_echo:{rel}:finding[{idx}]:value_fp={_fingerprint(matched_value)}"
                )
                break

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "scanned_files": scanned,
            "secret_env_names_checked": len(env_names),
            "secret_env_values_checked": len(env_values),
            "env_name_echoes": env_name_echoes,
            "env_value_echoes": env_value_echoes,
        },
        "metadata": {"gate": "report_secret_leak"},
    }
    out = sec / "report_secret_leak.json"
    write_json_report(out, report)
    print(f"REPORT_SECRET_LEAK_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
