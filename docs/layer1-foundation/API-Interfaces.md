# Glyphser API Interface Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Implementation.APIInterfaceContract`  
**Purpose (1 sentence):** Define deterministic, typed, versioned callable interfaces for kernel and core operators.  
**Spec Version:** `Glyphser.Implementation.APIInterfaceContract` | 2026-02-18 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** API contract specification and interoperability.

---

## 1) Header & Global Semantics

### 0.0 Identity
- **Algorithm:** `Glyphser.Implementation.APIInterfaceContract`
- **Purpose (1 sentence):** Deterministic API interface contract.
- **Spec Version:** `Glyphser.Implementation.APIInterfaceContract` | 2026-02-18 | Authors: Olejar Damir
- **Domain / Problem Class:** Typed API contracts.

### 0.A Objective Semantics
- This algorithm performs deterministic validation only; no optimization is involved.
- Objective type: N/A.
- Primary comparison rule: exact schema and signature equality.
- Invalid objective policy: schema mismatch is failure.

### 0.B Reproducibility Contract
- Seed space: `seed ∈ {0..2^64-1}` where applicable.
- PRNG family: inherited from calling operator.
- Randomness locality: no sampling in interface contract checks.
- Replay guarantee: replayable given `(spec_version, interface_hash)`.
- Replay token: `api_replay_t = SHA-256(CBOR_CANONICAL(["api_interfaces", [spec_version, interface_hash]]))`.

### 0.C Numeric Policy
- Numeric fields specify explicit scalar kinds (`uint64`, `float64`, etc.).
- Rounding mode / fast-math: N/A for contract validation.
- NaN/Inf policy: invalid unless explicitly allowed by API field definition.
- Approx-equality: exact type match; no implicit coercion.

### 0.D Ordering and Tie-Break Policy
- Parameter order is canonical and positional.
- Tie-break for map-like fields MUST follow canonical CBOR key ordering from `docs/layer1-foundation/Canonical-CBOR-Profile.md` (canonical encoded-key byte ordering per RFC 8949).

### 0.D.1 Canonicalization Procedure (Normative)
- Interface signatures MUST be represented as CBOR data-model objects and encoded with `CBOR_CANONICAL` from `docs/layer1-foundation/Canonical-CBOR-Profile.md`.
- Optional fields are represented by key omission (not implicit `null`) unless a consuming schema explicitly permits `null`.
- String content is consumed as provided by upstream contracts; canonicalization does not apply locale transforms.

### 0.E Parallel, Concurrency, and Reduction Policy
- Contract validation is deterministic and single-pass.
- No async behavior.

### 0.F Environment and Dependency Policy
- Reference runtime: language-agnostic schema validator.
- Dependencies: deterministic canonical CBOR canonicalization.
- Determinism level: `BITWISE` for signature serialization and hashes.
- Canonicalization procedure is normative and profile-bound to `CanonicalSerialization` in `docs/layer1-foundation/Canonical-CBOR-Profile.md`.

### 0.G Operator Manifest
- `Glyphser.Implementation.ValidateAPISignature`
- `Glyphser.Implementation.ValidateIOShape`
- `Glyphser.Implementation.ComputeInterfaceHash`
- `Glyphser.Error.Emit`

### 0.H Namespacing and Packaging
- Fully-qualified names required.
- Sidecar mapping (`operator -> module/function`) required.
- Sidecar mapping schema (normative): canonical CBOR map
  - key: `operator_fqn:string`
  - value: `{module:string, function:string}`.

### 0.I Outputs and Metric Schema
- Declared outputs: `(validation_report, interface_hash)`.
- Metrics: `validated_operators`, `schema_mismatches`, `hash`.
- Completion status: `success | failed`.

### 0.J Spec Lifecycle Governance
- Breaking signature change requires MAJOR bump.
- Backward-compatible field additions require MINOR bump.
- Equivalence target: E0.

### 0.K Failure and Error Semantics
- Abort-only with deterministic error record.
- Codes: `API_SIGNATURE_MISMATCH`, `API_SHAPE_MISMATCH`, `API_TYPE_MISMATCH`.

### 0.L Input/Data Provenance
- Input schemas must be versioned and hash-addressable.

---

### 0.Z EQC Mandatory Declarations Addendum
- `stochastic_used: false`
- `seed_space: N/A`
- `prng_family: N/A`
- `rng_ownership: N/A`
- `numeric_kernel: N/A`
- `tolerances: N/A`
- `determinism_level: BITWISE` (for signature serialization + hashes)
- `error_trace: inherited from docs/layer1-foundation/Error-Codes.md`
- `note: this contract performs deterministic validation only`

## 2) System Model

Numbering convention note:
- Section 1 uses EQC header field labels (`0.*`).
- Section 2 uses model partitions (`I.*`, `II.*`).
- This split is intentional and normative for EQC compatibility.

### I.A Persistent State
- `interface_registry: map<operator, signature>`.

### I.B Inputs and Hyperparameters
- `declared_interfaces`, `implemented_interfaces`.

### I.C Constraints and Feasible Set
- Unconstrained; validity determined by exact schema compatibility.

### I.D Transient Variables
- `diffs`, `validation_report`, `interface_hash`.

### I.E Invariants and Assertions
- Registry entries are unique and versioned.

### II.F Syscall Interface Registry (Concrete, Authoritative)
Canonical display note:
- `allowed_error_codes` values in this rendered table are shown in canonical ordered-array form from `contracts/operator_registry.cbor`.
- Signature computation always uses the canonical ordered array representation.
- `request_schema_digest` and `response_schema_digest` cells are `digest_ref` renderings; canonical signature preimage uses resolved bytes32 values.
- `Glyphser.Error.Emit` is included as a syscall operator because it is callable and listed in the operator manifest.
| surface | name | version | method | request_schema_digest | response_schema_digest | idempotent | side_effects | allowed_error_codes | signature_digest |
|---|---|---|---|---|---|---|---|---|---|
| `SYSCALL` | `Glyphser.Data.NextBatch` | v2 | syscall | `sha256:b3c93fdc0519e72c27a3203174fbb5ac8b96c760f1bdc739874ea6870ae8a500` | `sha256:a74f659e6edfc9a663a78d148981b27ee46f6685bc6786ed1ca7e5e7763b4fa3` | true | `["NONE"]` | `["BATCH_SIZE_INCONSISTENT","INVALID_DATASET_KEY","CARDINALITY_MISMATCH","GLOBAL_POSITION_EXCEEDS_CARDINALITY","INVALID_STAGE_TYPE"]` | `sha256:67069ace699a580ed23a01168b46d0242002d82f8d429266b195d3a459eb972f` |
| `SYSCALL` | `Glyphser.Model.Forward` | v2 | syscall | `sha256:82a1c1413fc3fd8176c351bb828315354fb3434760cdb4a47f30408f92f26fa7` | `sha256:d69a39c6e458a4803aff256e848784fddc34f6db4c5a963b5959fbc264076c09` | false | `["ADVANCES_RNG"]` | `["CONTRACT_VIOLATION","PRIMITIVE_UNSUPPORTED"]` | `sha256:17d85435fe2e601fe522b614938ea7853b9c36be14c8feb84f4e70e1e253bc74` |
| `SYSCALL` | `Glyphser.Model.ModelIR_Executor` | v1 | syscall | `sha256:a50166213aefcd3a51e2660cd50d4dca444353e4d3642c1cacc7300c158ef362` | `sha256:a9788d4553cee1d35d7f79c65d21cdf28d143a066152462568fa5e5d3ad36024` | false | `["ALLOCATES_MEMORY"]` | `["INVALID_IR","PRIMITIVE_UNSUPPORTED","CYCLE_DETECTED","SHAPE_MISMATCH","TMMU_ALLOCATION_FAILURE","CONTRACT_VIOLATION"]` | `sha256:ce1ec3e5cead31a92f46e79847332d3db0fdd824f2f3b6608987c77450a6de70` |
| `SYSCALL` | `Glyphser.DifferentialPrivacy.Apply` | v3 | syscall | `sha256:c788135091bca6dda0dfa6be1903fe534aba3ce8aba22802338f4557c2f62b2c` | `sha256:e4511aa77256d2b3984b25381f8a14e780a0f701bfeb5db134f06143607cb7d6` | false | `["ADVANCES_RNG","MUTATES_ACCOUNTANT"]` | `["PRIVACY_BUDGET_EXCEEDED","INVALID_DP_CONFIG","INVALID_GRADIENT","NAN_IN_SIGMA","ACCOUNTANT_OVERFLOW","ACCOUNTANT_DIVERGENCE","RNG_CONSUMPTION_VIOLATION"]` | `sha256:df574eb8b39a83a8107bce17dbcddbd3c1751aa51ccd6f9dcdd0e95ddab6b52f` |
| `SYSCALL` | `Glyphser.TMMU.PrepareMemory` | v2 | syscall | `sha256:1868515eb2e8b04486ca2a2a0aec0cad27e33a85e1c66369dbdb6dd72f3aa227` | `sha256:5602da41a9eb5e0d7ab21000bb82018688523f01987e498e186ba6854991df1e` | false | `["ALLOCATES_MEMORY"]` | `["INVALID_IR_SHAPES","LIVENESS_CYCLE","ADDRESS_COLLISION","ALLOCATION_OVERFLOW","ARENA_TOO_SMALL","ALIGNMENT_VIOLATION"]` | `sha256:87ad2acf49cc0081824d67a2b0838d03d3bd2f3f2d3ae19a9b07af50bc264b09` |
| `SYSCALL` | `Glyphser.Backend.LoadDriver` | v1 | syscall | `sha256:b9d299c7e1cd2bd04e499b1458b2bb935f47de74daf18652356fc36f117f76b1` | `sha256:c2a0b76a20abbe89e02cd7626c77e300d0f0373d6b47b9e437eec408727c9768` | false | `["PERFORMS_IO","NETWORK_COMM"]` | `["BACKEND_CONTRACT_VIOLATION"]` | `sha256:708fd111f6fc0a8f85853a4218ff9eba82ffc3da285266b15f6714a450728056` |
| `SYSCALL` | `Glyphser.IO.SaveCheckpoint` | v1 | syscall | `sha256:47d294c74846623fdf009597597bfc131190727f15959b846520ccc3162494df` | `sha256:ef98d3bdf59fafb396766c343ffd67b730175f43c34d7d7b64903993132ff430` | false | `["PERFORMS_IO"]` | `["CONTRACT_VIOLATION"]` | `sha256:7500cd45013f340439c196a8119f1da650f325f9b9fb22567574df80a78c5d77` |
| `SYSCALL` | `Glyphser.Checkpoint.Restore` | v1 | syscall | `sha256:87e869485275faea2aecf8a8cf8398ecb7452cb0c6df60327b4a1671c8948caf` | `sha256:1ac5f1b5313af3eeba05b0aa2e6df19358d7ee51f957fe07dcd29f4faca2c28a` | false | `["PERFORMS_IO","MUTATES_MODEL_STATE"]` | `["CONTRACT_VIOLATION"]` | `sha256:2ad8fce88d166dfbfd042dfd9e91e1e282e4f549cea088b141872d53a863ef89` |
| `SYSCALL` | `Glyphser.Error.Emit` | v1 | syscall | `sha256:fe80f62ef86ec79731ec8bf913a336651d0326851760667ed1e06c1adbf4bc6e` | `sha256:83e2decc3c6e418f3a61404f91c88cec96b5a2fb573d77fe3db98ffc548622d1` | false | `["PERFORMS_IO"]` | `["CONTRACT_VIOLATION"]` | `sha256:0cb1f29e7f28d98dc020d74fdac09b1d56e18e137e6a5f445447480bd450785c` |

### II.G Service API Registry (Concrete, Authoritative)
Canonical display note:
- `allowed_error_codes` values in this rendered table are shown in canonical ordered-array form from `contracts/operator_registry.cbor`.
| surface | name | version | method | request_schema_digest | response_schema_digest | idempotent | side_effects | allowed_error_codes | signature_digest |
|---|---|---|---|---|---|---|---|---|---|
| `SERVICE` | `Glyphser.Tracking.RunCreate` | v1 | service | `sha256:79f63d036b91c33bbd5a0a64468f93107f79b755e73810824d3877aeb6561fc1` | `sha256:658a3e66ec1cf259a71244bc535d7d4efa5fc648ca4aedf8686e50e2bfd29dad` | false | `["PERFORMS_IO"]` | `["CONTRACT_VIOLATION"]` | `sha256:f9912032a083a24960b3fce71bef84b6b6669bd4f1455143b793abd46c61d979` |
| `SERVICE` | `Glyphser.Tracking.RunStart` | v1 | service | `sha256:3c9f675dfcb5deb7de64eecff530e2a0d1ad327714e38b22db4b3a40834a319c` | `sha256:663474fa4ef7f6cbf299ef27426b09a36a57a05cde2af9775ccc470f91edf9c1` | false | `["PERFORMS_IO"]` | `["CONTRACT_VIOLATION"]` | `sha256:3bbc23354e81d350087a3eb11f45db4202d35b2c3a0d789917ce250c67d604ad` |
| `SERVICE` | `Glyphser.Tracking.RunEnd` | v1 | service | `sha256:2d7735c3a7d1f21b2966ef34279274fdeb2d5cdedf1295d06d69b46ffe6c44c1` | `sha256:e3fbb827b7df3c88ecbe534511e4a681c8f914b03314f45db615b0265f182767` | false | `["PERFORMS_IO"]` | `["CONTRACT_VIOLATION"]` | `sha256:61cffc6435589391694727d1950e9b897ecb4a9a1678ad318b7cb4863762bd8a` |
| `SERVICE` | `Glyphser.Tracking.MetricLog` | v1 | service | `sha256:e4dfe80e6d2e71cf3281f732fb4ce3bff8c8fb5cce4b339e0ffb0e10fbf2d705` | `sha256:dbeeadfcd9ce45b81acb44aede35acd0caebba6be61a1bf2b0775644c6812fc3` | false | `["PERFORMS_IO"]` | `["CONTRACT_VIOLATION"]` | `sha256:2bfc26d97f932a7f4dc99529872f54dcee07c1f37fa160dc1f09d4bbc0052553` |
| `SERVICE` | `Glyphser.Tracking.ArtifactPut` | v1 | service | `sha256:376c6ac9c8f23bd60de605af173aaedfb29f9a9772a16bc4319d5eaf2ca88212` | `sha256:8d5ec7401a722b52bffd442dc143be279636527005c45b7cde91ce186286f1b5` | false | `["PERFORMS_IO"]` | `["CONTRACT_VIOLATION"]` | `sha256:4c83219b6825bbbb8b64254328e6fa7d64e4eb04065f32e214ba7576fe0c3621` |
| `SERVICE` | `Glyphser.Tracking.ArtifactGet` | v1 | service | `sha256:aaa6f3df2d7f7837909b36fb6ffb8a7cb4e7137fa043c35d6d9ed441cd04400f` | `sha256:d2afbd6a00fe8ad77800be3bd21ece5e4508cccda15c614b80e648adb288d8f1` | true | `["PERFORMS_IO"]` | `["CONTRACT_VIOLATION"]` | `sha256:89c470402948fd7717c7a89074e466ccaa731270b28bd798c8ef4b3905521d83` |
| `SERVICE` | `Glyphser.Tracking.ArtifactList` | v1 | service | `sha256:390eb2cd44de8e5a8702e2e9ee5a9546fa6f3bad93ede910f191d0b5cafa9d99` | `sha256:32a01fe15e446238cd353af5b0fd517352c4584831062670e1a0d77567767a91` | true | `["PERFORMS_IO"]` | `["CONTRACT_VIOLATION"]` | `sha256:a02167e5e2a3f785190069b65127032dd2841544af82da03dd1d237fbdc38f40` |
| `SERVICE` | `Glyphser.Tracking.ArtifactTombstone` | v1 | service | `sha256:34be789a7612797a9bcac210bf5664724e7a1a10b6a1321cd2196b0378accbc5` | `sha256:269fe8e05ec1db5c082f7e3c6b1ef5a37a8e1ae65fd2cc9c9903b1dd3e8de5e1` | false | `["PERFORMS_IO"]` | `["CONTRACT_VIOLATION"]` | `sha256:668e41817d89f2aeb2af4e9394302cb935425450e4595c5db1965ed5d3f9ea22` |
| `SERVICE` | `Glyphser.Registry.VersionCreate` | v1 | service | `sha256:1535b143bf15d47cde6b95c1e8bd9d90018d9e631b8565007c3ff0f4c5eeb221` | `sha256:c422b8f784e0a458336a0d7eb7b5adb32d9608aef2d459359e99142bed3bed43` | false | `["PERFORMS_IO"]` | `["CONTRACT_VIOLATION"]` | `sha256:5690d2ee8d34c3407e33f14f25198d35af170150c663b5290f9f6460003a8f0e` |
| `SERVICE` | `Glyphser.Registry.StageTransition` | v1 | service | `sha256:e634b4adad159203c88a086e8194833a9b3a718f68bad60fdeec0c616f25e770` | `sha256:39ce69213d5b015a69485eed6bd9065065ae8981b55368c65f2148d0a8490a18` | false | `["PERFORMS_IO"]` | `["CONTRACT_VIOLATION"]` | `sha256:df171fad79b74e99a5cf98c98c0dd0d99891c6e28d2b21de21de12e797db46af` |
| `SERVICE` | `Glyphser.Monitor.Register` | v1 | service | `sha256:3812992f06cac5e8845b5707f18487a7abd1c18b797d0d17f0dbef2c5e535988` | `sha256:fc700ecfc6b59d532b0f2090fa9f3f9d5a25365503bad36df2bd7d17ace66605` | false | `["PERFORMS_IO"]` | `["CONTRACT_VIOLATION"]` | `sha256:0a5e9373bfba01ba4bbeddba689074a704d538e7ebe4e072a139cef99bbd4440` |
| `SERVICE` | `Glyphser.Monitor.Emit` | v1 | service | `sha256:063a9d6fbd2cc06ca6230a9dd42e740edec0ea0b76eae794c6695f239b9a35ff` | `sha256:6adacbfc76a20bed4a542e1df0090d662e51fb6e9b08ef1d67734dbc6de6d7f2` | false | `["PERFORMS_IO"]` | `["CONTRACT_VIOLATION"]` | `sha256:eb4d0698028761a1d5f75b66d7a67a758045aa33846d50296990722b30156550` |
| `SERVICE` | `Glyphser.Monitor.DriftCompute` | v1 | service | `sha256:84751ff5c4f6c4508d2eb3bf6b5fb382a43aeef11b15a7d5f10e392a50742d93` | `sha256:9976dd86b5801ea78df696947695ca62e1e9868f02dd36c2a8cdcbc5b793be3a` | true | `["NONE"]` | `["CONTRACT_VIOLATION"]` | `sha256:901881d54845698125611c9d87d11e7fa5419248a4caf8dbb839465dccfe25fb` |
| `SERVICE` | `Glyphser.Certificate.EvidenceValidate` | v1 | service | `sha256:1165b63ee12061a187b8bbbe0f55eb800d09f5c7ec1e7a45d02fc90ee594960a` | `sha256:b803f8990a492ff39515aa099d0d92297488a07501b37a613e43502afa17dc79` | true | `["NONE"]` | `["CONTRACT_VIOLATION"]` | `sha256:9d55661802f55dacd9695031acfeed3745f9a501b7db5606b814ad546116d5b1` |
| `SERVICE` | `Glyphser.Config.ManifestMigrate` | v1 | service | `sha256:12bfcae0d2cf5d76c722cd4f967eb4a250f2316fc5fc2173a96585f6684500e3` | `sha256:d54f71baddda92b26c3bbdad54037f9573a6d16763c437ff2d6250ddb7ac7ba7` | false | `["PERFORMS_IO"]` | `["CONTRACT_VIOLATION"]` | `sha256:29695a8e891b995033fc2508204991bb8cb28067965ebac7bfbe26478b40cc89` |
| `SERVICE` | `Glyphser.Checkpoint.CheckpointMigrate` | v1 | service | `sha256:3be7173771ea6e390239d664e137cc4a54db6fa696587a5bc3f514bdc7e35a57` | `sha256:70c2eaa4515e6662e32aee16a46c9055319fa6f61cb01ea18a7cb9d2b48dfe6f` | false | `["PERFORMS_IO"]` | `["CONTRACT_VIOLATION"]` | `sha256:ea0f1f735948058cd9893fe6f9c661ca578097c83c93780c624c4245dc576c59` |
| `SERVICE` | `Glyphser.Trace.TraceMigrate` | v1 | service | `sha256:a79b56d5d8b5629e62bfab67f08432459ffef04ae4beb121f3f098eee5a4365f` | `sha256:53a6622c6b83f35487826cf96e27b7b6cc9afc888d8afd4e76d03250de206e86` | false | `["PERFORMS_IO"]` | `["CONTRACT_VIOLATION"]` | `sha256:fe3709bad090dcd8f5f190649a7694bd26ca059e9a47b3eaf784d0268bf442ee` |
| `SERVICE` | `Glyphser.Import.LegacyFramework` | v1 | service | `sha256:64442d19eded7c78bc5b84301b0be39f5c6f3aee6dc35efe0db3cf5545a76d7c` | `sha256:8c834fc6ef6ce6a077d23903f51fc0ccab895f3b5762daf3fc03fd46fc566be5` | false | `["PERFORMS_IO"]` | `["CONTRACT_VIOLATION"]` | `sha256:20c8da5d2c5565476edc1c59ba209b14f19e0f4f3e71be86f4854f28abea0839` |

### II.H Schema/Signature Digest Rules (Normative)
- `SchemaDigest = SHA-256(CBOR_CANONICAL(schema_ast_normalized))`.
- `SignatureDigest` is defined normatively in `docs/layer1-foundation/Operator-Registry-Schema.md` (`sig` preimage with resolved bytes32 digests).
- Canonical schema sources must be stored under `schemas/` and used as the single source for digest generation in build/codegen.
- `schema_ast_normalized` (normative):
  - schema parsed into AST with resolved type aliases,
  - canonical field ordering (bytewise UTF-8 lexicographic by field name),
  - explicit optionality/default annotations materialized,
  - no implementation-specific metadata fields.

### II.I Canonical Operator Registry Binding (Normative)
- `contracts/operator_registry.cbor` is authoritative for interface metadata.
- Every row in syscall/service registries must match the corresponding artifact record exactly for:
  - `surface`, `request_schema_digest`, `response_schema_digest`, `signature_digest`,
  - `side_effects`, `allowed_error_codes`, `purity_class`, `required_capabilities`.
- This document is a rendered view; edits that are not reflected in the artifact are invalid.
- Rendered-table note:
  - `purity_class` and `required_capabilities` are authoritative in `contracts/operator_registry.cbor` but omitted in rendered tables here for readability.

### II.J Capability/RBAC Binding (Normative)
- Every callable operator must declare `required_capabilities` in the canonical operator registry.
- Authorization verdict per call must be deterministic:
  - `authz_query_hash = SHA-256(CBOR_CANONICAL([tenant_id, [principal_id, operator_id, sorted(required_capabilities), authz_policy_hash, capability_matrix_hash]]))`.
  - `authz_decision_hash = SHA-256(CBOR_CANONICAL([authz_query_hash, [verdict_enum, granted_capabilities_hash, decision_reason_code]]))`.
- Denied calls must emit a deterministic failure record and trace event with `authz_decision_hash`.

### II.K Kernel Syscall Registry (Kernel Subset View)
- This table is the kernel syscall subset view and must match `docs/layer2-specs/Glyphser-Kernel-v3.22-OS.md` section 4 (1:1 operator membership).
- For any operator also present in `II.F`, digest fields MUST be byte-identical to `II.F`.
- Each listed operator must resolve to concrete request/response schema digests and signature digest in `contracts/operator_registry.cbor`.
| name | method | request_schema_digest | response_schema_digest | signature_digest |
|---|---|---|---|---|
| `Glyphser.OS.Bootstrap` | syscall | `sha256:6b95add4346e37b63e64c7e208a7df8f4965e372878b8b9fd4fed7c5bbd403b7` | `sha256:d9625678d8addcaf15db3e69d1ffa9e954a64bb290d4981087a5837bce2c87af` | `sha256:08c1cb8901ce5f30ec8015c5eed6efd43061269ef899e03f8a493b54f4a335c7` |
| `Glyphser.OS.ResolvePath` | syscall | `sha256:f82201a6830a4c6d980a9b4b43978c87f7122478d60be2dfbb8a052deb00783b` | `sha256:e647055a824d66af8290fadbe67fad3ca74f8b25c452d2848ed2d427bba80997` | `sha256:d1351c580e2a35476e067c55ed84657c51d716176e24ec14afa9b3e60f9b9a7e` |
| `Glyphser.OS.NamespaceEnter` | syscall | `sha256:2a87e448ed17daf1a91417ecf6bb467a1d379b6c85b0299f5d882d6065620633` | `sha256:8d28371559d3bd93aa1dc4db75b922db61ab64789ccb1b3a468c9e252f6117d9` | `sha256:edd3f2c3428542cf0bfe2eef09c0189da81eb4cbeda72dec97880474d3088682` |
| `Glyphser.Data.Manifest` | syscall | `sha256:3654426af7930039cad3d1dc0369450f7f18066c718f9a186867c1a9f619c3e2` | `sha256:78a4b828924c20cfd65a2112f2ddefeee17c7a60cdffa4a3d3061f8888aa81e1` | `sha256:a6ed8cf76086a6ac859048e40f5980c02c797917039b4f85539169c2a2a60a71` |
| `Glyphser.Data.ValidateManifest` | syscall | `sha256:c1f88fca6f77de2cc6bd833f478e774d2a7430ffbad7367f03f4aeffded23e26` | `sha256:b8d90fedcca9d9ffbce84a11c1c2a48e5722ac3499116d893f94a55e8296239d` | `sha256:6a7868616da975c611ac763a815fe897481b70ad8b888f8bff209233c89b6bf8` |
| `Glyphser.Data.NextBatch` | syscall | `sha256:b3c93fdc0519e72c27a3203174fbb5ac8b96c760f1bdc739874ea6870ae8a500` | `sha256:a74f659e6edfc9a663a78d148981b27ee46f6685bc6786ed1ca7e5e7763b4fa3` | `sha256:67069ace699a580ed23a01168b46d0242002d82f8d429266b195d3a459eb972f` |
| `Glyphser.Data.RegisterDataset` | syscall | `sha256:8e46cc4203902d52e8543728f848463fe1147a106349fe55c251fc9900371b20` | `sha256:8c69578f99e296e93a31b23a15be300c9a1e4e8c16afe55923b8f8054c999aca` | `sha256:fa4fca34ee532474b5ebb5cdbfba175fed2eaadbe4d5e99cbbd4a47387420989` |
| `Glyphser.Data.ImportAndRegister` | syscall | `sha256:d7d5be587bcdcc3459b7873757323b45818a9a0881b4603f8d3a8e5994a13839` | `sha256:caca94241bc539142fabc502bdcb3153aa1592f9c241335397b392076e506adc` | `sha256:a69a029f9fed4e9f654c6d54a3bc2e54285f01285b8d556cf339742ec81eb5ef` |
| `Glyphser.Model.Forward` | syscall | `sha256:82a1c1413fc3fd8176c351bb828315354fb3434760cdb4a47f30408f92f26fa7` | `sha256:d69a39c6e458a4803aff256e848784fddc34f6db4c5a963b5959fbc264076c09` | `sha256:17d85435fe2e601fe522b614938ea7853b9c36be14c8feb84f4e70e1e253bc74` |
| `Glyphser.Model.ExpandPreset` | syscall | `sha256:a29fb645799b57ea4a4032a9a29697bf51ff20ee2469af83098973c2e1fb0826` | `sha256:662de6db6e9b14bf13168b79137682e783b60eb605d9e5610210766195e331e7` | `sha256:8b58dca0a2345b5d115d81187589ec0d61388a19d8d94f3b5cdd5c2334534f83` |
| `Glyphser.Model.ApplyFineTune` | syscall | `sha256:ab5fec71b1c0ed85d7def95b9ca4a93512bfadc76694ad56380c947a88ce4679` | `sha256:f7bfe9be3307d5cf1eb847c5a4908ee959686c238a0903e2e490e3898b77a643` | `sha256:840971d67ece4e5b7eef6eb5d68c1fb5bcac5b61181798a966ba527f5291272a` |
| `Glyphser.Objective.TotalLoss` | syscall | `sha256:9b83b6707b2fa85f58f49ff5a1c66114b1bd8997d89e7402c1146f9d871ea736` | `sha256:1a712c624d506411a4f89b0c50817a7d6fa2aebd7bc960886fc5e00e21c19ddc` | `sha256:2d7e17c8b906d090f7edb238571f68d6f36409a2e886bc80bdc41cdaa33c77d3` |
| `Glyphser.Optimizer.Update` | syscall | `sha256:b67f9f7943effca758fe10599372e960112fe27e689b81fff9d510ef3210a54e` | `sha256:44bc40731fe3f283a666c65c806b6513709608ce8f86cd73575f72fea5768cb5` | `sha256:f5163784a6f0c3e0ab7f9d93ee7652348264809600fc1bdca121ce22707e033f` |
| `Glyphser.Module.RegisterCustom` | syscall | `sha256:4fdba7baab89d6c7ff5c293cc5ddabbae21af8e0f757b0412b7e3ef3e9a3953a` | `sha256:6ffd1b926a3cc7cda04ca017481d05090fba6742d2527714c5de84e1375065a4` | `sha256:dc812a5845fc78fb7b7eae7d42b1b90f7d840d99c5c4cd1d83d09767c166d405` |
| `Glyphser.Policy.Evaluate` | syscall | `sha256:bdaeefcfdafff6ba8d79ee757f08f9d5c5ef9cd4c34110ae9a3c73ec245e4da2` | `sha256:ee125a4968ba99cea329a14b95948b8b27d4cd3d7b63752c8957ecd98609d4dc` | `sha256:d3deb27e807de01491da8f3286a03aa2a95e36c66525cefdc7d08f455396fb34` |
| `Glyphser.Contract.Validate` | syscall | `sha256:0ff020e0e3a53351c77cb0879226c6d51ee5b871027cae906bbfb99e3df1b4c4` | `sha256:43d29709c190ba8f50bad8e0cdf6e473a7a6c7c81ef5fc1c8b3377e3534601df` | `sha256:a29d999bcd747ce0a666e965492bec241a58c0e476a3dcaddf345f64c3740132` |
| `Glyphser.IO.WriteTape` | syscall | `sha256:9f05a18d391747a0fc91def1097592cb2d73d5214650ad37ad48382de2f7be28` | `sha256:c194ac7ca5ed44b138e0a5833d8345d531853f0621e85bd837ee2559de133a62` | `sha256:3f8e9fa6f43b5b95b55806068e662c63669df472a6f2fb9f11be9a6af7ec80b9` |
| `Glyphser.IO.SaveCheckpoint` | syscall | `sha256:47d294c74846623fdf009597597bfc131190727f15959b846520ccc3162494df` | `sha256:ef98d3bdf59fafb396766c343ffd67b730175f43c34d7d7b64903993132ff430` | `sha256:7500cd45013f340439c196a8119f1da650f325f9b9fb22567574df80a78c5d77` |
| `Glyphser.Certificate.WriteExecutionCertificate` | syscall | `sha256:5d67c20d00f6b0c3a6b8e0f3617eebdfc5eca398aed4539b7a63427be372b772` | `sha256:ffcda8c4913eba63cdb31a4b0fd3e79d9e790cb02a29129f551a5ea35de4e0c7` | `sha256:e2b8389dc808da6e631f4d6365ca256c4c0005bf756674b8357c519b3b067514` |
| `Glyphser.State.Journal` | syscall | `sha256:73d6f8f0a2ed2405131cd52a1e8cdd7ac5cdb77391a14054a35ed5a6d66ed0ec` | `sha256:968806f83eb4ec37d8c9f3f76d7a9207ecd1547b7cbf6522582dff57ef29467d` | `sha256:77af6f21db7ad774735a92323cf0635d3576bcdd943abe316aa084540d1dde34` |
| `Glyphser.Termination.Check` | syscall | `sha256:ef7d9d1d2378d1acbf85fd86af5596ecc360fb7a79e63e5c7f220f04150dce7d` | `sha256:2e764c0500e07cc3465e9fa5e71158d9151409bd12d5439414c88831ceaafefc` | `sha256:ec35105bda624ff9d225c800f34e93fdf51c82ad67e928b2c78cfc1a16ef31ef` |
| `Glyphser.Fingerprint.StateFingerprint` | syscall | `sha256:af18d3615139f226da1b6b8f7646e65547681ff49e24346eb7b23403964a004a` | `sha256:d16eb6e8964c2096a4d1632228554c776ac40166f75b910dc7d4caff2e3fac6e` | `sha256:54763a526ff78f14ffe3dec8c0944a9e9d26007f582eedfc85e798887b986669` |
| `Glyphser.Fingerprint.Functional` | syscall | `sha256:6347e5c15b9898e03120ac6a4d9a4a54ba601ac608fb10860c35dae071526c39` | `sha256:ac13b14a64283e8f257ffe80067dd72693968601a05b19a015a3a8bd0dfc500d` | `sha256:64ccf71e54020c3a17cafe24458c0147614310448b64a44749f792bcddc4a6da` |
| `Glyphser.Error.Emit` | syscall | `sha256:fe80f62ef86ec79731ec8bf913a336651d0326851760667ed1e06c1adbf4bc6e` | `sha256:83e2decc3c6e418f3a61404f91c88cec96b5a2fb573d77fe3db98ffc548622d1` | `sha256:0cb1f29e7f28d98dc020d74fdac09b1d56e18e137e6a5f445447480bd450785c` |
| `Glyphser.Distributed.Setup` | syscall | `sha256:7e8fdb0852b617888a3eb423787a9b5e1ba206173a1dda37550139d8d1ade0a2` | `sha256:3f8563b15d2050973185087fa89be664d5cf032bd1ebad0830840e0372778999` | `sha256:8f9f8367e7a00cd1b3fe87a5a9238b761b8c09ede2ec835c4c1abb0f55916702` |
| `Glyphser.Evaluation.Run` | syscall | `sha256:290a073ce9830f68151186bffe02bf6711e79949c4b9871decb3ed1fe9237d8b` | `sha256:bd29a04ed4a4297f712751d5ea1760ae79c5eb16d666708cf8e50bb3cf49b3a5` | `sha256:07d194d0b634a85eef1ca7b6fe4bd1786037a0e6b8a8504850af6533735e95f5` |
| `Glyphser.Security.AttestTEE` | syscall | `sha256:c6f8eada24a2482866d5bae0149c6707851aa7d94b886876ea849a59e55c2889` | `sha256:690253b660f5956bd6f38d5cd16b2f5ddb6a860cdf0053ac3d1b24f5d0233d30` | `sha256:ab930860204463c24c2df98764c6410f6207062a23238448ec3ea84f08148927` |
| `Glyphser.Verifiable.CommitFunctional` | syscall | `sha256:5f7682174b5ff972d570acc219ff07197bd49120980d087993ed42e12053572b` | `sha256:93e5ba69c82f516cd9806b8f9be68e8ae048c102e45ebd8cefea33a7be4ac6b0` | `sha256:8a6eedab6cf4a79fec3a17a23b4c47e91f6bfce1e979ae69210de6ae93b3862c` |
| `Glyphser.DifferentialPrivacy.Apply` | syscall | `sha256:c788135091bca6dda0dfa6be1903fe534aba3ce8aba22802338f4557c2f62b2c` | `sha256:e4511aa77256d2b3984b25381f8a14e780a0f701bfeb5db134f06143607cb7d6` | `sha256:df574eb8b39a83a8107bce17dbcddbd3c1751aa51ccd6f9dcdd0e95ddab6b52f` |
| `Glyphser.Backend.LoadDriver` | syscall | `sha256:b9d299c7e1cd2bd04e499b1458b2bb935f47de74daf18652356fc36f117f76b1` | `sha256:c2a0b76a20abbe89e02cd7626c77e300d0f0373d6b47b9e437eec408727c9768` | `sha256:708fd111f6fc0a8f85853a4218ff9eba82ffc3da285266b15f6714a450728056` |
| `Glyphser.Pipeline.Dispatch` | syscall | `sha256:c4ba86ac3ba9f9e0c322771914848eb72e9c5e36c5a9c8828f8d6f55d3de44bb` | `sha256:451c011e029b5d115e95092cc1952c36a8000a72b65e119bd1dda15d77ce18ca` | `sha256:5c3541f522edf71475ad465ea07303273dbb301db258baa63d4b6d7e25fe911d` |
| `Glyphser.Inference.RunBatch` | syscall | `sha256:413088da6e718570c050892c3e272823a4bc3be2bd85638d228fbeca14306d0f` | `sha256:d7eb4aa78a41d586676f1eb67ac4e3e7404d91648a8c2002b3caf7b899c08cba` | `sha256:d8c6c6c790701ea9f9e8e1a370549e0e059e4520a7414bbb404a56efdf3483be` |
| `Glyphser.Model.Backward` | syscall | `sha256:bc7e0699d6f8a6c778f0cf4dbbaa73cc0f9389682de1512c979608262d11d725` | `sha256:b631a6ac19ba9aa0612db577717dff96a6eebf3fe25aacd3230744b444d78858` | `sha256:703bd22df1f08ac39226c51b08bce7c73396b484c440737497dc79bda672e7af` |
| `Glyphser.Symbolic.Augment` | syscall | `sha256:f1e889eb31bd7d78329a46a40c0ccd21d35db27eb12c38d40d06fa919bace7aa` | `sha256:9edf3ecb9d21824f916f116aac19f05f17b622def37f6641210c6dad409d670e` | `sha256:810cc5b6ce8161a364e3b80f678fb8f3459790a5bdd9346be3bcd87922afec1e` |
| `Glyphser.Security.VerifyCertificate` | syscall | `sha256:11c8108318f8db27dc96b6ecd689fa171d0ea4f20b2aa82dced7e61ea0e9c526` | `sha256:8e953036cfdd7db445cd2ca698ad3aa4735c457e5053c4fc24ff0134ac7bde76` | `sha256:d4d5727241d591689241c55e5056964aba2885b5e543da86c251309dfe2cbbdb` |
| `Glyphser.Transition.SwitchState` | syscall | `sha256:7bbf2cd20736ac4f1c737302f57db2529f93c3d9db2ff83d0df607c887c9e4de` | `sha256:8c47c41abc7289ee18fd528c70289c3cde0d9214f362791ba3713fb0defab9e1` | `sha256:f1ecdd9a111f4333fbf2915bcde851c29deef1aea4f9398726e34da44c8c7452` |

---

## 3) Initialization

1. Load declared interfaces.
2. Canonicalize schemas.
3. Build interface registry.

---

## 4) Operator Manifest

- `Glyphser.Implementation.ValidateAPISignature`
- `Glyphser.Implementation.ValidateIOShape`
- `Glyphser.Implementation.ComputeInterfaceHash`
- `Glyphser.Error.Emit`

---

## 5) Operator Definitions

External operator reference: `Glyphser.Error.Emit` is defined normatively in `docs/layer1-foundation/Error-Codes.md` and imported by reference.

**Operator:** `Glyphser.Implementation.ValidateAPISignature`  
**Category:** IO  
**Signature:** `(declared, implemented -> report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** exact field/type/order validation.  
**Output schema (`report`, normative):** `{success:bool, mismatches:array<string>}` where each mismatch is a deterministic field-path string.
**Preconditions / Postconditions:** inputs canonicalized.  
**Edge cases:** missing optional fields.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** field traversal order is canonical CBOR key order of the CBOR-encoded field-name text strings (see `Canonical-CBOR-Profile.md`).  
**Complexity note:** O(total_fields).  
**Failure behavior:** emit deterministic mismatch record.  
**Dependencies:** canonical schema encoder.  
**Test vectors:** matching/mismatching signatures.

**Operator:** `Glyphser.Implementation.ValidateIOShape`  
**Category:** IO  
**Signature:** `(signature, sample_payload -> ok:bool)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** validates payload type/shape contracts.  
**Preconditions / Postconditions:** signature exists.  
**Edge cases:** optional and nullable fields.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** deterministic key traversal.  
**Complexity note:** O(payload_size).  
**Failure behavior:** `API_SHAPE_MISMATCH`.  
**Dependencies:** schema validator.  
**Test vectors:** representative payload set.

**Operator:** `Glyphser.Implementation.ComputeInterfaceHash`  
**Category:** IO  
**Signature:** `(registry -> interface_hash)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** construct `registry_map` as a canonical CBOR map (`operator_fqn -> signature_object`) and compute `interface_hash = SHA-256(CBOR_CANONICAL(["api_interfaces", registry_map]))`.  
**Preconditions / Postconditions:** unique registry keys.  
**Edge cases:** empty registry.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** map ordering is canonical CBOR key ordering; no ad-hoc secondary sort is allowed.  
**Complexity note:** O(registry_size).  
**Failure behavior:** abort on hash serialization failure.  
**Dependencies:** canonical serializer + hash function.  
**Test vectors:** fixed registry hash snapshots.

---

## 6) Procedure

```text
1. ValidateAPISignature(declared, implemented)
2. ValidateIOShape(...) on representative payloads
3. ComputeInterfaceHash(registry)
4. Return report + hash
```

---

## 7) Trace & Metrics

### Logging rule
Each validation run emits deterministic mismatch and summary records.

### Trace schema
- `run_header`: spec_version, interface_count
- `iter`: operator, check_type, result
- `run_end`: status, interface_hash

### Metric schema
- `validated_operators`, `schema_mismatches`, `hash`

### Comparability guarantee
Comparable iff identical schema keys/typing, identical interface hash domain tag (`"api_interfaces"`), and identical canonical serialization profile/version (`CanonicalSerialization`).

---

## 8) Validation

#### VII.A Lint rules (mandatory)
Passes symbol completeness, no hidden globals, deterministic ordering, trace compliance.

#### VII.B Operator test vectors (mandatory)
Includes exact signature and payload conformance vectors.

#### VII.C Golden traces (mandatory)
Golden hash snapshots for known interface sets.

---

## 9) Refactor & Equivalence

#### VIII.A Equivalence levels
- E0 required.

#### VIII.B Allowed refactor categories
- Validator implementation refactor preserving outputs and hashes.

#### VIII.C Equivalence test procedure (mandatory)
Compare full report and interface hash.

---

## 10) Checkpoint/Restore

### Checkpoint contents
- interface registry snapshot + hash.

### Serialization
- deterministic canonical CBOR.

### Restore semantics
- restored registry yields identical validation outputs.

---
## 11) External API Artifact Generation Addendum (Normative)
- API interface registry MUST be translatable to:
  - OpenAPI artifact bundle,
  - Protobuf artifact bundle.
- Hash typing for generated artifact identities:
  - `ObjectDigest(obj) = SHA-256(CBOR_CANONICAL(obj))`
  - `openapi_bundle_hash` and `protobuf_bundle_hash` are `ObjectDigest` identities (not domain-separated commitments).
- Generation identity:
  - `openapi_bundle_hash = ObjectDigest(openapi_bundle)`
  - `protobuf_bundle_hash = ObjectDigest(protobuf_bundle)`
- Generated SDK requirement:
  - at minimum Python/Go/TypeScript SDK generation must consume these artifacts without altering canonical request/response semantics.
- Conformance requirement:
  - generated clients must pass interface conformance suites with the same canonicalization and signature-digest rules as runtime operators.
- Conformance catalog identity:
  - `api_artifact_conformance_catalog_hash = SHA-256(CBOR_CANONICAL(["api_artifact_conformance", [test_vector_set_hash, conformance_runner_version_hash, canonical_profile_id]]))`.
- Deterministic round-trip requirement:
  - generated client -> server stub -> canonical request/response bytes MUST be byte-identical to runtime canonicalization rules under `CanonicalSerialization`.
- Interoperability bridge reference:
  - `docs/layer4-implementation/Interoperability-Standards-Bridge.md`.
