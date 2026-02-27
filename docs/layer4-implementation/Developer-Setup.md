# Glyphser Developer Setup Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Implementation.DeveloperSetup`  
**Purpose (1 sentence):** Define deterministic local developer environment setup and verification steps for implementing Glyphser components.  
**Spec Version:** `Glyphser.Implementation.DeveloperSetup` | 2026-02-19 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Local development bootstrap and environment consistency.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Implementation.DeveloperSetup`
- **Purpose (1 sentence):** Deterministic developer setup contract.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary objective: minimize setup drift and non-reproducible local runs.
### 0.B Reproducibility Contract
- Replayable given `(lockfile_hash, toolchain_hash, env_manifest_hash, determinism_profile_hash)`.
### 0.C Numeric Policy
- N/A except deterministic parsing of versions and hashes.
### 0.D Ordering and Tie-Break Policy
- Setup checks execute in fixed order.
### 0.E Parallel, Concurrency, and Reduction Policy
- Validation may run in parallel; verdict merge order is deterministic.
### 0.F Environment and Dependency Policy
- Canonical runtime pins must match `docs/layer1-foundation/Dependency-Lock-Policy.md` and `docs/layer1-foundation/Environment-Manifest.md`.
### 0.G Operator Manifest
- `Glyphser.Dev.Setup.ValidateHost`
- `Glyphser.Dev.Setup.ValidateToolchain`
- `Glyphser.Dev.Setup.ValidateEnvManifest`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- `Glyphser.Dev.Setup.*`
### 0.I Outputs and Metric Schema
- Outputs: `(setup_report, env_manifest_hash)`
- Metrics: `checks_passed`, `checks_failed`
### 0.J Spec Lifecycle Governance
- Required check changes are MAJOR.
### 0.K Failure and Error Semantics
- Abort on failed required setup checks.
### 0.L Input/Data Provenance
- Host/toolchain facts must be captured via canonical probes.

---
## 2) System Model
### I.A Persistent State
- Local cache of validated setup report.
### I.B Inputs and Hyperparameters
- Host OS info, Python/toolchain versions, lockfiles, config.
### I.C Constraints and Feasible Set
- Valid iff required versions/hashes/flags match policy.
### I.D Transient Variables
- Probe outputs and normalized diagnostics.
### I.E Invariants and Assertions
- No hidden defaults; all env vars used by runtime are declared.

---
## 3) Initialization
1. Load dependency and environment contracts.
2. Probe host/runtime/toolchain.
3. Build deterministic setup checklist.

---
## 4) Operator Manifest
- `Glyphser.Dev.Setup.ValidateHost`
- `Glyphser.Dev.Setup.ValidateToolchain`
- `Glyphser.Dev.Setup.ValidateEnvManifest`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
**Operator:** `Glyphser.Dev.Setup.ValidateHost`  
**Signature:** `(host_probe -> host_report)`  
**Purity class:** PURE  
**Determinism:** deterministic.

**Operator:** `Glyphser.Dev.Setup.ValidateToolchain`  
**Signature:** `(toolchain_probe, lock_policy -> toolchain_report)`  
**Purity class:** PURE  
**Determinism:** deterministic.

**Operator:** `Glyphser.Dev.Setup.ValidateEnvManifest`  
**Signature:** `(env_manifest, profile -> validation_report)`  
**Purity class:** PURE  
**Determinism:** deterministic.

---
## 6) Procedure
```text
1. ValidateHost
2. ValidateToolchain
3. ValidateEnvManifest
4. Emit setup_report
```

---
## 7) Trace & Metrics
### Logging rule
- Setup emits deterministic validation records.
### Trace schema
- `run_header`: setup_version, host_id_hash
- `iter`: check_id, status
- `run_end`: setup_status, env_manifest_hash
### Metric schema
- `checks_passed`, `checks_failed`
### Comparability guarantee
- Comparable iff same setup spec + probe inputs.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- Required checks complete and deterministic ordering enforced.
#### VII.B Operator test vectors (mandatory)
- Valid/invalid host and toolchain fixtures.
#### VII.C Golden traces (mandatory)
- Golden setup traces.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for setup verdict and report hash.
#### VIII.B Allowed refactor categories
- Probe implementation changes preserving normalized outputs.
#### VIII.C Equivalence test procedure (mandatory)
- Exact compare of setup reports.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- Last validated setup report hash and manifest hash.
### Serialization
- Canonical CBOR.
### Restore semantics
- Restored setup context must reproduce identical validation verdict.

---
## 11) Time-to-First-Success Profile Promise (Normative)
- `core` profile setup target:
  - deterministic quickstart completion in under 10 seconds on supported baseline hardware.
- `enterprise` and `regulated` profiles:
  - may require additional controls, but MUST declare incremental setup deltas relative to `core`.
- Setup reports MUST include:
  - profile id,
  - time-to-first-success measurement (informational),
  - deterministic verdict fields unaffected by timing variance.
- Onboarding companion references:
  - `docs/layer4-implementation/Gentle-Introduction.md`
  - `docs/layer4-implementation/Hello-World-End-to-End-Example.md`
  - `docs/layer4-implementation/Common-Pitfalls-Guide.md`
