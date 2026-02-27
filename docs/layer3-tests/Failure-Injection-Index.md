# Glyphser Failure Injection Scenario Index
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Test.FailureInjectionIndex`
**Purpose (1 sentence):** Provide a deterministic index from mandatory chaos scenarios to invariants, recovery procedures, and proof-pack expectations.
**Spec Version:** `Glyphser.Test.FailureInjectionIndex` | 2026-02-21 | Authors: Olejar Damir
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Test.FailureInjectionIndex`
- **Purpose (1 sentence):** Deterministic failure-injection scenario index.
- **Spec Version:** `Glyphser.Test.FailureInjectionIndex` | 2026-02-21 | Authors: Olejar Damir
- **Domain / Problem Class:** resilience verification index.
### 0.A Objective Semantics
- Ensure each mandatory scenario has explicit invariant + proof-pack mapping.
### 0.B Reproducibility Contract
- Replayable given `(scenario_registry_hash, invariant_catalog_hash, recovery_policy_hash)`.
### 0.C Numeric Policy
- N/A.
### 0.D Ordering and Tie-Break Policy
- Scenarios ordered by `scenario_id`.
### 0.E Parallel, Concurrency, and Reduction Policy
- Independent scenarios may run in parallel; verdict set merged deterministically.
### 0.F Environment and Dependency Policy
- Scenario execution references fixed fixture/environment hashes.
### 0.G Operator Manifest
- `Glyphser.Test.InjectFault`
- `Glyphser.Test.RunRecovery`
- `Glyphser.Test.ValidateRecoveryOutcome`
### 0.H Namespacing and Packaging
- Scenario index namespace: `tests/failure_injection/index/`.
### 0.I Outputs and Metric Schema
- Outputs: `(scenario_index_report, scenario_index_hash)`.
### 0.J Spec Lifecycle Governance
- Required scenario set updates are MAJOR-governed.
### 0.K Failure and Error Semantics
- Missing invariant/proof-pack mapping is deterministic failure.
### 0.L Input/Data Provenance
- Sources: `Failure-Injection-Scenarios.md`, recovery runbooks, release gates.

## 2) Scenario Mapping Table (Normative)
| scenario_id | invariants | recovery_procedure_refs | proof_pack_fields | acceptable_outcomes_by_profile |
|---|---|---|---|---|
| `network_partition_primary_quorum` | quorum restored, no committed-state fork | `docs/layer4-implementation/Distributed-Failure-Recovery-Guide.md` | `scenario_id,recovery_transcript_hash,invariant_results,final_verdict` | core: pass/fail logged; enterprise/regulated: pass required |
| `artifact_store_partial_unavailable` | no data loss, deterministic retry semantics | `docs/layer4-implementation/Disaster-Recovery-Operations-Runbook.md` | same as above + artifact consistency summary hash | core: pass/fail logged; enterprise/regulated: pass required |
| `wal_corruption_truncated_tail` | deterministic rollback or finalize path | `docs/layer2-specs/Run-Commit-WAL.md` | same as above + wal_recovery_hash | regulated requires proof-pack pass |
| `wal_corruption_checksum_mismatch` | chain integrity detection and deterministic abort | `docs/layer2-specs/Run-Commit-WAL.md` | same as above + wal_chain_validation_hash | regulated requires proof-pack pass |

## 3) Index Hash
- `scenario_index_hash = SHA-256(CBOR_CANONICAL(["failure_index", rows]))`.

## 6) Procedure
```text
1. Load mandatory scenario set from Failure-Injection-Scenarios.
2. Resolve invariant and recovery procedure mappings.
3. Validate required proof-pack field coverage.
4. Emit scenario_index_report and scenario_index_hash.
```
