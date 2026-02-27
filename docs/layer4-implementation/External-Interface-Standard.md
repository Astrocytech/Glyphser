# Glyphser External Interface Standard
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.API.ExternalInterfaceStandard`
**Purpose (1 sentence):** Define generated external API artifacts, derivation rules, versioning, and conformance obligations.
**Spec Version:** `Glyphser.API.ExternalInterfaceStandard` | 2026-02-21 | Authors: Olejar Damir
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.API.ExternalInterfaceStandard`
- **Purpose (1 sentence):** Deterministic external API interoperability contract.
- **Spec Version:** `Glyphser.API.ExternalInterfaceStandard` | 2026-02-21 | Authors: Olejar Damir
- **Domain / Problem Class:** interface generation and third-party integration.
### 0.A Objective Semantics
- Generated interfaces are normative artifacts, not advisory exports.
### 0.B Reproducibility Contract
- Replayable given `(operator_registry_root_hash, interface_contract_hash, generator_version_hash)`.
### 0.C Numeric Policy
- N/A.
### 0.D Ordering and Tie-Break Policy
- Endpoint and message ordering derived deterministically from canonical operator registry order.
### 0.E Parallel, Concurrency, and Reduction Policy
- Generator steps may parallelize; emitted artifacts must be byte-identical.
### 0.F Environment and Dependency Policy
- Canonical profile: `CanonicalSerialization`.
### 0.G Referenced Operators (Template-only)
- Template-only: listed operators are roadmap entry-points and are non-normative until each has a contract definition and a registry row.
- `Glyphser.Product.GenerateExternalInterfaces`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- `interfaces/openapi/`, `interfaces/protobuf/`, `sdk/<lang>/`.
### 0.I Outputs and Metric Schema
- Outputs: `(openapi_bundle_hash, protobuf_bundle_hash, sdk_bundle_hash, interface_conformance_hash)`.
### 0.J Spec Lifecycle Governance
- Compatibility rules are MAJOR-governed.
### 0.K Failure and Error Semantics
- Mismatched canonicalization is deterministic failure.
### 0.L Input/Data Provenance
- Source-of-truth inputs: `docs/layer1-foundation/API-Interfaces.md`, `contracts/operator_registry.cbor`.

## 2) Derivation Rules (Normative)
- OpenAPI/Protobuf/SDK artifacts MUST be generated only from canonical operator registry + API interface contract.
- Manual edits to generated artifacts are non-conformant.
- Client round-trip conformance suite is mandatory:
  - generated client -> server stub -> canonical request/response bytes must match runtime canonicalization.

## 3) Compatibility Policy (Normative)
- `stable`: backward compatible within MAJOR.
- `lts`: long support window per lifecycle policy.
- `experimental`: no compatibility guarantee.
- See: `docs/layer4-implementation/API-Lifecycle-and-Deprecation-Policy.md`.

## 4) Conformance Identity (Normative)
- `interface_conformance_hash = SHA-256(CBOR_CANONICAL(["iface_conf", [test_vector_set_hash, runner_version_hash, openapi_bundle_hash, protobuf_bundle_hash, sdk_bundle_hash]]))`.

## 6) Procedure
```text
1. Load canonical operator registry and API interface contract.
2. Generate OpenAPI, Protobuf, and SDK bundles deterministically.
3. Run round-trip client conformance suite.
4. Emit bundle hashes and interface_conformance_hash.
```
