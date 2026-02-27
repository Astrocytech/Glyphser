# Glyphser Target Architecture Profile
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Implementation.TargetArchitectureProfile`
**Purpose (1 sentence):** Fix the primary codegen targets, runtime integration contracts, and build/test entrypoints for the initial Glyphser implementation.
**Spec Version:** `Glyphser.Implementation.TargetArchitectureProfile` | 2026-02-27 | Authors: Olejar Damir
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Implementation target selection and integration contracts.

---
## 1) Target Decisions (Normative)
### 1.1 Primary Generation Targets
- **Language/runtime:** Python 3.12.
- **Packaging:** importable `glyphser` package in `src/`, with script entrypoints in `scripts/`.
- **Artifacts:** JSON and CBOR artifacts under `contracts/`, `fixtures/`, `goldens/`, and `vectors/`.
- **Scope:** CPU-only, single-node runtime for the reference implementation.

### 1.2 Secondary Targets (Deferred)
- Additional runtimes (GPU, distributed) are deferred until after codegen templates stabilize.
- Service surfaces are deferred; the initial target is local, file-based execution.

### 1.3 Project Layout (Normative)
- Canonical layout is defined by `docs/layer4-implementation/Repo-Layout-and-Interfaces.md`.
- Code generation must respect the namespace and directory boundaries in that contract.

---
## 2) Runtime Integration Contracts (Normative)
### 2.1 Logging and Tracing
- Trace records are written as deterministic JSON sidecars per `docs/layer2-specs/Trace-Sidecar.md`.
- Trace hash computation must match `src/glyphser/trace/compute_trace_hash.py` and `docs/layer4-implementation/Canonical-Hashing-Reference.md`.

### 2.2 Metrics and Experiment Tracking
- Metrics reporting and experiment tracking follow `docs/layer2-specs/Experiment-Tracking.md`.
- Metrics emission must remain deterministic and content-addressed where required.

### 2.3 AuthZ and Capability Enforcement
- Capability checks follow `docs/layer2-specs/AuthZ-Capability-Matrix.md`.
- Generated wrappers must enforce `required_capabilities` in `contracts/operator_registry.cbor`.

### 2.4 Persistence and Artifact Stores
- Local filesystem persistence is the default for the reference implementation.
- Storage adapter behavior is governed by `docs/layer4-implementation/Artifact-Store-Adapter-Guide.md`.

---
## 3) Build/Test Scripts (Normative)
### 3.1 Required Local Entry Points
- Schema gate: `python tools/schema_gate.py`
- Registry gate: `python tools/registry_gate.py`
- Conformance suite: `python tools/conformance/cli.py run`
- Conformance report: `python tools/conformance/cli.py report`
- Hello-core runnable: `python scripts/run_hello_core.py`

### 3.2 CI Entry Points
- CI must execute the same commands as local entrypoints.
- Gate policy is defined in `docs/layer4-implementation/Build-and-CI-Matrix.md`.

---
## 4) Dependency Lock Policy (Normative)
- Lock policy is defined by `docs/layer1-foundation/Dependency-Lock-Policy.md`.
- The canonical lockfile name for this project is `requirements.lock`.
- Release bundles must include lockfile hash commitments as required by `docs/layer2-specs/Execution-Certificate.md`.
- Local development may use editable installs, but release evidence must be computed from the locked environment.

---
## 5) Validation
- Target profile changes are MAJOR if they alter the primary language/runtime or canonical layout.
- Any deviation from these targets must be declared in release evidence and gating reports.
