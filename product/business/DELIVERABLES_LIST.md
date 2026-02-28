# Client Deliverables (Fixed Scope)

## Summary
Each engagement produces a concise, reproducible evidence package that a third party can re‑run.

## Core Deliverables
- Executive summary (1 page): scope, verdict, and key findings.
- Verification report: PASS/FAIL results and hash confirmations.
- Evidence bundle: logs, hashes, and artifact manifests needed for replay.
- Issue list (if any): reproducible steps, affected contract sections, severity.

## Artifact Set
- Conformance report (`evidence/`) with deterministic results.
- Verification inputs/outputs (manifest, vectors, trace hash, certificate hash).
- Repro instructions (exact commands + environment notes).

## What Is Not Included
- Implementation changes or code fixes.
- Custom feature development.
- Infrastructure provisioning.
- Long‑term support beyond the fixed scope.

## Formats
- Markdown report(s) + JSON/CBOR artifacts.
- Signed report only if explicitly agreed.
