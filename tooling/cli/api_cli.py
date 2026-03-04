#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from runtime.glyphser.api.runtime_api import (
    RuntimeApiConfig,
    RuntimeApiService,
)

ROOT = Path(__file__).resolve().parents[2]


def _service(state_path: str | None) -> RuntimeApiService:
    path = Path(state_path) if state_path else ROOT / "evidence" / "state" / "api" / "state.json"
    return RuntimeApiService(RuntimeApiConfig(root=ROOT, state_path=path))


def _print_json(payload: dict) -> int:
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Glyphser public API CLI (v1).")
    parser.add_argument("--state-path", default="", help="Path for local API state store.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    submit = sub.add_parser("submit", help="Submit a job.")
    submit.add_argument("--payload-file", required=True)
    submit.add_argument("--token", required=True)
    submit.add_argument("--scope", required=True)
    submit.add_argument("--idempotency-key", default="")

    status = sub.add_parser("status", help="Get job status.")
    status.add_argument("--job-id", required=True)
    status.add_argument("--token", required=True)
    status.add_argument("--scope", required=True)

    evidence = sub.add_parser("evidence", help="Get job evidence summary.")
    evidence.add_argument("--job-id", required=True)
    evidence.add_argument("--token", required=True)
    evidence.add_argument("--scope", required=True)

    replay = sub.add_parser("replay", help="Run replay check for a job.")
    replay.add_argument("--job-id", required=True)
    replay.add_argument("--token", required=True)
    replay.add_argument("--scope", required=True)

    args = parser.parse_args(argv)
    svc = _service(args.state_path)

    try:
        if args.cmd == "submit":
            payload = json.loads(Path(args.payload_file).read_text(encoding="utf-8"))
            return _print_json(
                svc.submit_job(
                    payload=payload,
                    token=args.token,
                    scope=args.scope,
                    idempotency_key=args.idempotency_key or None,
                )
            )
        if args.cmd == "status":
            return _print_json(svc.status(job_id=args.job_id, token=args.token, scope=args.scope))
        if args.cmd == "evidence":
            return _print_json(svc.evidence(job_id=args.job_id, token=args.token, scope=args.scope))
        if args.cmd == "replay":
            return _print_json(svc.replay(job_id=args.job_id, token=args.token, scope=args.scope))
        raise ValueError(f"unknown command: {args.cmd}")
    except Exception as exc:  # pragma: no cover - command-line path
        print(f"API_CLI_ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
