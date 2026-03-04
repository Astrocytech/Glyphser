#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import tempfile
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from runtime.glyphser.api.runtime_api import (
    RuntimeApiConfig,
    RuntimeApiService,
    _canonical_json,
)

ROOT = Path(__file__).resolve().parents[3]


WAIVER_ADR = "evidence/repro/decisions/ADR-2026-03-01-m12-resource-gap-temporary-waiver.md"


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _runtime_meta() -> dict[str, Any]:
    return {
        "platform": platform.platform(),
        "kernel": platform.release(),
        "python": platform.python_version(),
        "timestamp_utc": datetime.now(UTC).isoformat(),
    }


def _prepare_minimal_evidence_root(root: Path) -> None:
    (root / "conformance" / "reports").mkdir(parents=True, exist_ok=True)
    (root / "artifacts" / "bundles").mkdir(parents=True, exist_ok=True)
    (root / "evidence" / "repro").mkdir(parents=True, exist_ok=True)
    (root / "conformance" / "reports" / "latest.json").write_text(
        json.dumps({"status": "PASS"}) + "\n", encoding="utf-8"
    )
    line = "abc123  hello-core-bundle.tar.gz\n"
    (root / "artifacts" / "bundles" / "hello-core-bundle.sha256").write_text(line, encoding="utf-8")
    (root / "evidence" / "repro" / "hashes.txt").write_text(line, encoding="utf-8")


def _class_from_checks(checks: list[dict[str, Any]]) -> tuple[str, str, str]:
    statuses = [c["status"] for c in checks]
    if any(s == "FAIL" for s in statuses):
        return "FAIL", "E2", "At least one service reproducibility check failed."
    if any(s == "BLOCKED" for s in statuses):
        return "BLOCKED", "E2", "At least one service reproducibility check is blocked."
    classes = [c["classification"] for c in checks]
    overall_class = "E0" if all(c == "E0" for c in classes) else "E1"
    return "PASS", overall_class, "All service reproducibility checks pass."


def main() -> int:
    parser = argparse.ArgumentParser(description="Milestone 15 service-level reproducibility checks.")
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--requests", type=int, default=128)
    parser.add_argument(
        "--output-dir",
        default=str(ROOT / "evidence" / "repro" / "milestone-15-service-reproducibility"),
    )
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    with tempfile.TemporaryDirectory(prefix="glyphser-m15-") as td:
        temp_root = Path(td) / "repo"
        state_path = Path(td) / "state.json"
        _prepare_minimal_evidence_root(temp_root)
        svc = RuntimeApiService(RuntimeApiConfig(root=temp_root, state_path=state_path))

        payload_a = {"payload": {"job": "svc-demo", "params": {"x": 1, "y": 2}}}
        payload_b = {"payload": {"params": {"y": 2, "x": 1}, "job": "svc-demo"}}
        canon_a = _canonical_json(payload_a)
        canon_b = _canonical_json(payload_b)
        c_status = "PASS" if canon_a == canon_b else "FAIL"
        checks.append(
            {
                "check": "canonical_request_equivalence",
                "status": c_status,
                "classification": "E0" if c_status == "PASS" else "E2",
                "reason": "Canonical JSON matches for semantically equivalent payloads."
                if c_status == "PASS"
                else "Canonical JSON mismatch.",
                "details": {"canonical_a": canon_a, "canonical_b": canon_b},
            }
        )

        first = svc.submit_job(payload=payload_a, token="token-a", scope="jobs:write")
        second = svc.submit_job(payload=payload_b, token="token-a", scope="jobs:write")
        same_job = first["job_id"] == second["job_id"]
        checks.append(
            {
                "check": "canonical_submit_determinism",
                "status": "PASS" if same_job else "FAIL",
                "classification": "E0" if same_job else "E2",
                "reason": "Equivalent canonical payloads map to identical job_id."
                if same_job
                else "Equivalent payloads produced different job_id.",
                "details": {"job_id_a": first["job_id"], "job_id_b": second["job_id"]},
            }
        )

        idem_key = "idem-m15-key"
        idem_results = [
            svc.submit_job(
                payload=payload_a,
                token="token-a",
                scope="jobs:write",
                idempotency_key=idem_key,
            )
            for _ in range(5)
        ]
        idem_ids = sorted({r["job_id"] for r in idem_results})
        idem_ok = len(idem_ids) == 1
        checks.append(
            {
                "check": "idempotency_single_thread",
                "status": "PASS" if idem_ok else "FAIL",
                "classification": "E0" if idem_ok else "E2",
                "reason": "Repeated idempotent submits return same job_id."
                if idem_ok
                else "Idempotent submits diverged.",
                "details": {"job_ids": idem_ids},
            }
        )

        keys = [f"batch-key-{i % 4}" for i in range(args.requests)]

        def _submit(ix: int) -> dict[str, Any]:
            payload = {"payload": {"job": "svc-concurrent", "index": ix % 4}}
            return svc.submit_job(
                payload=payload,
                token="token-a",
                scope="jobs:write",
                idempotency_key=keys[ix],
            )

        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            results = list(ex.map(_submit, range(args.requests)))

        by_key: dict[str, set[str]] = {}
        for i, r in enumerate(results):
            by_key.setdefault(keys[i], set()).add(r["job_id"])
        concurrent_ok = all(len(v) == 1 for v in by_key.values())
        checks.append(
            {
                "check": "idempotency_concurrent_load",
                "status": "PASS" if concurrent_ok else "FAIL",
                "classification": "E1" if concurrent_ok else "E2",
                "reason": "Concurrent idempotent submissions are stable per key."
                if concurrent_ok
                else "Concurrent idempotent submissions diverged.",
                "details": {k: sorted(v) for k, v in by_key.items()},
            }
        )

        replay_job = idem_results[0]["job_id"]
        ev_a = svc.evidence(replay_job, token="token-a", scope="evidence:read")
        ev_b = svc.evidence(replay_job, token="token-a", scope="evidence:read")
        rp_a = svc.replay(replay_job, token="token-a", scope="replay:run")
        rp_b = svc.replay(replay_job, token="token-a", scope="replay:run")
        evidence_repro = ev_a == ev_b
        replay_repro = rp_a == rp_b and rp_a.get("replay_verdict") == "PASS"
        checks.append(
            {
                "check": "evidence_replay_stability",
                "status": "PASS" if evidence_repro and replay_repro else "FAIL",
                "classification": "E1" if evidence_repro and replay_repro else "E2",
                "reason": "Evidence and replay responses are stable and PASS under repeat calls."
                if evidence_repro and replay_repro
                else "Evidence or replay responses changed across repeated calls.",
                "details": {
                    "evidence_a": ev_a,
                    "evidence_b": ev_b,
                    "replay_a": rp_a,
                    "replay_b": rp_b,
                },
            }
        )

    overall_status, overall_class, overall_reason = _class_from_checks(checks)

    report = {
        "milestone": 15,
        "profile": "service_reproducibility",
        "status": overall_status,
        "classification": overall_class,
        "reason": overall_reason,
        "checks": checks,
        "meta": _runtime_meta(),
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "repro-classification.json").write_text(
        json.dumps(
            {
                "milestone": 15,
                "profile": "service_reproducibility",
                "classification": overall_class,
                "status": overall_status,
                "reason": overall_reason,
                "excluded_operators": [],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    pair_rows = [
        {
            "pair": "service_api__vs__service_api_replay",
            "status": overall_status,
            "classification": overall_class,
            "reason": overall_reason,
            "checks": [c["check"] for c in checks],
        }
    ]
    (out_dir / "pair-matrix.json").write_text(
        json.dumps({"pairs": pair_rows}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "env-matrix.json").write_text(
        json.dumps(report["meta"], indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    coverage = {
        "milestone": 15,
        "service_surface": ["submit_job", "status", "evidence", "replay"],
        "checks": [c["check"] for c in checks],
        "status": overall_status,
    }
    (out_dir / "coverage-summary.json").write_text(
        json.dumps(coverage, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    waivers: list[dict[str, Any]] = []
    if (ROOT / WAIVER_ADR).exists():
        waivers.append(
            {
                "id": "M12_TEMP_RESOURCE_GAP",
                "adr": WAIVER_ADR,
                "scope": "Milestones 13-15 execution unblocked while Milestone 12 is BLOCKED.",
                "status": "ACTIVE",
            }
        )
    (out_dir / "waivers.json").write_text(
        json.dumps({"waivers": waivers}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    conformance_hashes: dict[str, Any] = {"status": overall_status}
    results_path = ROOT / "evidence" / "conformance" / "results" / "latest.json"
    report_path = ROOT / "evidence" / "conformance" / "reports" / "latest.json"
    if results_path.exists():
        conformance_hashes["conformance_results"] = {
            "path": "evidence/conformance/results/latest.json",
            "sha256": _sha256_file(results_path),
        }
    if report_path.exists():
        conformance_hashes["conformance_report"] = {
            "path": "evidence/conformance/reports/latest.json",
            "sha256": _sha256_file(report_path),
        }
    (out_dir / "conformance-hashes.json").write_text(
        json.dumps(conformance_hashes, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    playbook_hooks = {
        "hooks": [
            {
                "event": "idempotency_violation",
                "severity": "high",
                "action": "freeze write path and inspect audit chain",
            },
            {
                "event": "replay_verdict_fail",
                "severity": "high",
                "action": "trigger reproducibility incident workflow",
            },
            {
                "event": "canonicalization_mismatch",
                "severity": "medium",
                "action": "block deploy and diff canonical payload bytes",
            },
        ]
    }
    (out_dir / "incident-playbook-hooks.json").write_text(
        json.dumps(playbook_hooks, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    summary = [
        "# Milestone 15: End-to-End Service Reproducibility",
        "",
        f"Status: {overall_status}",
        f"Classification: {overall_class}",
        f"Reason: {overall_reason}",
        "",
        "## Checks",
    ] + [f"- {c['check']}: {c['status']} ({c['classification']})" for c in checks]
    (out_dir / "summary.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    (out_dir / "known-limitations.md").write_text(
        "# Known Limitations (Milestone 15)\n\n"
        "- Current service reproducibility checks run in-process against file-backed state.\n"
        "- Multi-process/remote transport fault tolerance is tracked as follow-up hardening.\n",
        encoding="utf-8",
    )

    milestone_manifest = {
        "milestone": 15,
        "slug": "service-reproducibility",
        "owner": "Astrocytech/Glyphser",
        "target_date": "2026-07-12",
        "dependencies": [14],
        "waiver_dependencies": [12],
        "profiles": ["service_api"],
        "result": overall_status,
        "classification": overall_class,
        "evidence_dir": "evidence/repro/milestone-15-service-reproducibility/",
    }
    (out_dir / "milestone.json").write_text(
        json.dumps(milestone_manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "status": overall_status,
                "classification": overall_class,
                "reason": overall_reason,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if overall_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
