"""Public CLI entrypoint for Glyphser."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
from pathlib import Path
from typing import Any

from glyphser.internal.evidence_writer import write_evidence
from glyphser.internal.manifest_builder import build_manifest
from glyphser.public.verify import verify
from runtime.glyphser.cli import main as runtime_main
from runtime.glyphser.trace.compute_trace_hash import compute_trace_hash
from tooling.scripts import run_hello_core

ROOT = Path(__file__).resolve().parents[1]


def _sha256_canonical_json(payload: dict[str, Any]) -> str:
    data = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def _verify_hello_core() -> dict[str, Any]:
    with contextlib.redirect_stdout(io.StringIO()):
        rc = run_hello_core.main()
    fixture_root = ROOT / "artifacts" / "inputs" / "fixtures" / "hello-core"
    golden_path = ROOT / "specs" / "examples" / "hello-core" / "hello-core-golden.json"
    interface_hash_path = ROOT / "specs" / "contracts" / "interface_hash.json"

    trace_records = json.loads((fixture_root / "trace.json").read_text(encoding="utf-8"))
    certificate = json.loads((fixture_root / "execution_certificate.json").read_text(encoding="utf-8"))
    expected = json.loads(golden_path.read_text(encoding="utf-8"))["expected_identities"]
    interface_hash = json.loads(interface_hash_path.read_text(encoding="utf-8"))["interface_hash"]

    actual = {
        "trace_final_hash": compute_trace_hash(trace_records),
        "certificate_hash": _sha256_canonical_json(certificate),
        "interface_hash": interface_hash,
    }
    status = "PASS" if (rc == 0 and actual == expected) else "FAIL"
    return {
        "status": status,
        "fixture": "hello-core",
        "evidence_dir": str(fixture_root),
        "expected": expected,
        "actual": actual,
        "evidence_files": [
            str(fixture_root / "trace.json"),
            str(fixture_root / "checkpoint.json"),
            str(fixture_root / "execution_certificate.json"),
        ],
    }


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object in {path}")
    return payload


def _cmd_verify(args: argparse.Namespace) -> int:
    if args.target == "hello-core":
        payload = _verify_hello_core()
        if args.format == "json":
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(f"VERIFY {payload['fixture']}: {payload['status']}")
            print(f"Evidence: {payload['evidence_dir']}")
            print(f"Trace hash: {payload['actual']['trace_final_hash']}")
            print(f"Certificate hash: {payload['actual']['certificate_hash']}")
            print(f"Interface hash: {payload['actual']['interface_hash']}")
            if args.tree:
                print("Evidence files:")
                for path in payload["evidence_files"]:
                    print(f"  - {path}")
        return 0 if payload["status"] == "PASS" else 1

    if not args.model:
        raise ValueError("--model is required unless target is 'hello-core'")

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


def _cmd_run(args: argparse.Namespace) -> int:
    if args.example != "hello":
        raise ValueError("supported examples: hello")
    verify_args = argparse.Namespace(
        target="hello-core",
        model=None,
        input=None,
        format=args.format,
        tree=args.tree,
    )
    return _cmd_verify(verify_args)


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
    verify_cmd.add_argument("target", nargs="?", help="Named fixture target (for example: hello-core).")
    verify_cmd.add_argument("--model", help="Path to model IR JSON file.")
    verify_cmd.add_argument("--input", help="Path to input JSON file.")
    verify_cmd.add_argument("--format", choices=["json", "text"], default="json")
    verify_cmd.add_argument("--tree", action="store_true", help="Print evidence file tree for fixture verification.")

    run_cmd = sub.add_parser("run", help="Run quick built-in example.")
    run_cmd.add_argument("--example", default="hello", help="Example id (currently: hello).")
    run_cmd.add_argument("--format", choices=["json", "text"], default="text")
    run_cmd.add_argument("--tree", action="store_true", help="Print evidence file tree.")

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
    if args.cmd == "run":
        return _cmd_run(args)
    if args.cmd == "snapshot":
        return _cmd_snapshot(args)
    if args.cmd == "runtime":
        forwarded = args.args
        if forwarded and forwarded[0] == "--":
            forwarded = forwarded[1:]
        return runtime_main(forwarded)
    raise ValueError(f"unknown command: {args.cmd}")


__all__ = ["main"]


if __name__ == "__main__":
    raise SystemExit(main())
