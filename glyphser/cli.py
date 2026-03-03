"""Public CLI entrypoint for Glyphser."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from glyphser.internal.evidence_writer import write_evidence
from glyphser.internal.manifest_builder import build_manifest
from glyphser.public.verify import verify
from runtime.glyphser.cli import main as runtime_main


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object in {path}")
    return payload


def _cmd_verify(args: argparse.Namespace) -> int:
    model = _load_json(Path(args.model))
    input_data = _load_json(Path(args.input)) if args.input else {}

    result = verify(model=model, input_data=input_data)
    payload = {
        "status": "PASS",
        "digest": result.digest,
        "output": result.output,
    }
    if args.format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"VERIFY: PASS {result.digest}")
    return 0


def _cmd_snapshot(args: argparse.Namespace) -> int:
    model = _load_json(Path(args.model))
    input_data = _load_json(Path(args.input)) if args.input else {}

    result = verify(model=model, input_data=input_data)
    manifest = build_manifest(
        model=model,
        input_data=input_data,
        output=result.output,
        digest=result.digest,
    )
    out_path = Path(args.out)
    write_evidence(out_path, manifest)

    payload = {
        "status": "PASS",
        "digest": result.digest,
        "snapshot": str(out_path),
    }
    if args.format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"SNAPSHOT: PASS {result.digest} -> {out_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Glyphser public CLI.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    verify_cmd = sub.add_parser("verify", help="Run deterministic verification for a model JSON.")
    verify_cmd.add_argument("--model", required=True, help="Path to model IR JSON file.")
    verify_cmd.add_argument("--input", help="Path to input JSON file.")
    verify_cmd.add_argument("--format", choices=["json", "text"], default="json")

    snapshot_cmd = sub.add_parser("snapshot", help="Write a verification snapshot manifest.")
    snapshot_cmd.add_argument("--model", required=True, help="Path to model IR JSON file.")
    snapshot_cmd.add_argument("--input", help="Path to input JSON file.")
    snapshot_cmd.add_argument("--out", required=True, help="Output path for snapshot JSON.")
    snapshot_cmd.add_argument("--format", choices=["json", "text"], default="json")

    # Keep advanced operational commands available without exposing them as default UX.
    runtime_cmd = sub.add_parser("runtime", help="Run advanced runtime CLI commands (doctor/setup/run/certify).")
    runtime_cmd.add_argument("args", nargs=argparse.REMAINDER)

    args = parser.parse_args(argv)
    if args.cmd == "verify":
        return _cmd_verify(args)
    if args.cmd == "snapshot":
        return _cmd_snapshot(args)
    if args.cmd == "runtime":
        forwarded = args.args
        if forwarded and forwarded[0] == "--":
            forwarded = forwarded[1:]
        return runtime_main(forwarded)
    raise ValueError(f"unknown command: {args.cmd}")


__all__ = ["main"]
