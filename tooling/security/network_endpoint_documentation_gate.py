#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

POLICY = ROOT / "governance" / "security" / "network_endpoint_inventory.json"
POLICY_KEY_RE = re.compile(r"(?:^|_)(?:domain|domains|url|urls|endpoint|endpoints|host|hosts)(?:$|_)", re.IGNORECASE)
DOMAIN_RE = re.compile(r"^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}$", re.IGNORECASE)
HTTPS_RE = re.compile(r"https://([a-z0-9.-]+)", re.IGNORECASE)


def _normalize_endpoint(text: str) -> str | None:
    value = str(text).strip().lower()
    if not value:
        return None
    if value.startswith(("https://", "http://")):
        host = (urlparse(value).hostname or "").strip().lower().strip(".")
        return host if DOMAIN_RE.fullmatch(host) else None
    host = value.split("/")[0].strip().strip(".")
    if DOMAIN_RE.fullmatch(host):
        return host
    return None


def _extract_script_endpoints() -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for path in sorted((ROOT / "tooling" / "security").rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        domains = sorted(
            {
                normalized
                for raw in HTTPS_RE.findall(text)
                if (normalized := _normalize_endpoint(f"https://{raw}")) is not None
            }
        )
        if domains:
            rel = str(path.relative_to(ROOT)).replace("\\", "/")
            found[rel] = domains
    return found


def _extract_policy_endpoints() -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for path in sorted((ROOT / "governance" / "security").glob("*.json")):
        if path == POLICY:
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue

        domains: set[str] = set()
        stack: list[tuple[list[str], object]] = [([], payload)]
        while stack:
            key_path, value = stack.pop()
            if isinstance(value, dict):
                for key, item in value.items():
                    stack.append((key_path + [str(key)], item))
                continue
            if isinstance(value, list):
                for idx, item in enumerate(value):
                    stack.append((key_path + [str(idx)], item))
                continue
            if not isinstance(value, str):
                continue
            key_names = [part for part in key_path if not part.isdigit()]
            if not key_names:
                continue
            path_expr = ".".join(key_names)
            if not POLICY_KEY_RE.search(path_expr):
                continue
            normalized = _normalize_endpoint(value)
            if normalized:
                domains.add(normalized)

        if domains:
            rel = str(path.relative_to(ROOT)).replace("\\", "/")
            found[rel] = sorted(domains)
    return found


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not POLICY.exists():
        findings.append("missing_network_endpoint_inventory_policy")
        policy_payload: dict[str, object] = {}
    else:
        policy_payload = json.loads(POLICY.read_text(encoding="utf-8"))
        if not isinstance(policy_payload, dict):
            findings.append("invalid_network_endpoint_inventory_policy")
            policy_payload = {}

    sig = POLICY.with_suffix(".json.sig")
    if not sig.exists():
        findings.append("missing_network_endpoint_inventory_policy_signature")
    else:
        sig_text = sig.read_text(encoding="utf-8").strip()
        verified = artifact_signing.verify_file(POLICY, sig_text, key=artifact_signing.current_key(strict=False))
        if not verified:
            verified = artifact_signing.verify_file(POLICY, sig_text, key=artifact_signing.bootstrap_key())
        if not verified:
            findings.append("invalid_network_endpoint_inventory_policy_signature")

    documented = {
        normalized
        for item in policy_payload.get("documented_endpoints", [])
        if isinstance(item, str) and (normalized := _normalize_endpoint(item)) is not None
    }
    if not documented:
        findings.append("missing_documented_endpoints_entries")

    observed_by_source: dict[str, list[str]] = {}
    observed_by_source.update(_extract_script_endpoints())
    observed_by_source.update(_extract_policy_endpoints())

    observed: set[str] = set()
    for source, values in observed_by_source.items():
        for domain in values:
            observed.add(domain)
            if domain not in documented:
                findings.append(f"undocumented_network_endpoint:{source}:{domain}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "observed_endpoint_count": len(observed),
            "documented_endpoint_count": len(documented),
            "sources_with_endpoints": len(observed_by_source),
        },
        "metadata": {"gate": "network_endpoint_documentation_gate"},
        "observed_by_source": observed_by_source,
    }
    out = evidence_root() / "security" / "network_endpoint_documentation_gate.json"
    write_json_report(out, report)
    print(f"NETWORK_ENDPOINT_DOCUMENTATION_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
