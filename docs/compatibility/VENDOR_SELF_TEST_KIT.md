# Vendor Self-Test Kit

Status: DRAFT

## Purpose
Provide a self-service verification checklist for vendors.

## Steps
1. Run `python tools/verify_doc_artifacts.py`.
2. Run `python tools/conformance/cli.py run`.
3. Run `python scripts/run_hello_core.py`.
4. Bundle artifacts and hashes via `python tools/build_release_bundle.py`.

## Submission
- Provide conformance report, bundle hash, and environment manifest.
