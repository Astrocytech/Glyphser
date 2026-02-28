# Persistent Storage Adapter Contract (Milestone 19)

## Purpose
Define deterministic persistence and recovery requirements for run-state storage adapters.

## Contract Surface
- Adapter MUST persist state as versioned records.
- Adapter MUST maintain append-only WAL semantics for recovery replay.
- Adapter MUST support checkpoint write, backup export, and restore import.
- Adapter MUST quarantine corrupted state artifacts before replay recovery.

## Required Fields
- `schema_version` (integer, required)
- `state` (object, required)
- `state_hash` (sha256 hash of canonical state, required for checkpoints)
- `event_hash` (sha256 hash of canonical event, required for WAL records)

## Determinism Requirements
- WAL replay order is deterministic by file order.
- Canonical JSON serialization must use sorted keys and fixed separators.
- Restored state hash from a valid checkpoint MUST equal original state hash.

## Compatibility and Migration
- Schema version upgrades require an explicit migration path.
- Unsupported schema versions MUST hard-fail and emit recovery error.
- Cross-version replay compatibility changes require major contract revision.

## Security and Operations Baseline
- Persisted state/checkpoint transport and storage must be encrypted in supported prod profiles.
- Residency, retention, and key custody controls are profile-governed.

