# Glyphser Command Reference Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Implementation.CommandReference`  
**Purpose (1 sentence):** Define canonical command entrypoints and deterministic invocation patterns for development, testing, replay, and release workflows.  
**Spec Version:** `Glyphser.Implementation.CommandReference` | 2026-02-19 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Operational command governance.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Implementation.CommandReference`
- **Purpose (1 sentence):** Canonical command contract.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary objective: eliminate command ambiguity across environments.
### 0.B Reproducibility Contract
- Replayable given `(command_id, args_hash, env_manifest_hash, toolchain_hash)`.
### 0.C Numeric Policy
- Exit codes and counters are exact integers.
### 0.D Ordering and Tie-Break Policy
- Multi-step command workflows execute in fixed sequence.
### 0.E Parallel, Concurrency, and Reduction Policy
- Parallel command groups must define deterministic result merge.
### 0.F Environment and Dependency Policy
- Commands must run under validated setup.
### 0.G Operator Manifest
- `Glyphser.CLI.ValidateCommand`
- `Glyphser.CLI.ExecuteCommand`
- `Glyphser.CLI.ReportCommandResult`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- `glyphser <subcommand>` canonical form.
### 0.I Outputs and Metric Schema
- Outputs: `(command_report, exit_code)`
- Metrics: `commands_run`, `commands_failed`
### 0.J Spec Lifecycle Governance
- Required command signature changes are MAJOR.
### 0.K Failure and Error Semantics
- Invalid command forms fail deterministically.
### 0.L Input/Data Provenance
- Command inputs and outputs must be traceable by hashes.

---
## 2) System Model
### I.A Persistent State
- Command registry and help schema.
### I.B Inputs and Hyperparameters
- command id, args, env, profile.
### I.C Constraints and Feasible Set
- Valid iff command matches registered signature.
### I.D Transient Variables
- execution diagnostics.
### I.E Invariants and Assertions
- Command docs and actual signatures must match.

---
## 3) Initialization
1. Load command registry.
2. Parse invocation.
3. Validate against command schema.

---
## 4) Operator Manifest
- `Glyphser.CLI.ValidateCommand`
- `Glyphser.CLI.ExecuteCommand`
- `Glyphser.CLI.ReportCommandResult`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
**Operator:** `Glyphser.CLI.ValidateCommand`  
**Signature:** `(argv, command_registry -> validation_report)`  
**Purity class:** PURE  
**Determinism:** deterministic.

**Operator:** `Glyphser.CLI.ExecuteCommand`  
**Signature:** `(validated_command -> command_result)`  
**Purity class:** IO  
**Determinism:** deterministic under fixed inputs.

**Operator:** `Glyphser.CLI.ReportCommandResult`  
**Signature:** `(command_result -> command_report)`  
**Purity class:** PURE  
**Determinism:** deterministic.

---
## 6) Procedure
```text
1. ValidateCommand
2. ExecuteCommand
3. ReportCommandResult
4. Return (command_report, exit_code)
```

---
## 7) Trace & Metrics
### Logging rule
- Commands emit deterministic invocation/result records.
### Trace schema
- `run_header`: command_id, args_hash
- `iter`: step_id, status
- `run_end`: exit_code, result_hash
### Metric schema
- `commands_run`, `commands_failed`
### Comparability guarantee
- Comparable iff same command id, args, and env hash.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- Every documented command has a valid schema.
#### VII.B Operator test vectors (mandatory)
- Valid/invalid invocation vectors.
#### VII.C Golden traces (mandatory)
- Golden command execution traces.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for exit code and report hash.
#### VIII.B Allowed refactor categories
- CLI parser/runtime refactors preserving command semantics.
#### VIII.C Equivalence test procedure (mandatory)
- Exact compare for frozen command fixtures.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- Command workflow cursor and partial outputs.
### Serialization
- Canonical CBOR.
### Restore semantics
- Resumed command workflow yields same final exit and report.
