# Project File Inventory

Generated: 2026-02-28 17:10:55 UTC

Scope: Full repository tree excluding transient local cache directories (`.git`, `.venv`, `.pytest_cache`, `__pycache__`, lint/type caches).

## Full Tree Structure
```text
.
├── .github
│   └── workflows
│       ├── conformance-gate.yml
│       ├── push-button.yml
│       ├── registry-gate.yml
│       └── schema-gate.yml
├── artifacts
│   ├── bundles
│   │   ├── hello-core-bundle.sha256
│   │   └── hello-core-bundle.tar.gz
│   ├── expected
│   │   └── goldens
│   │       ├── checkpoint-restore
│   │       │   ├── checkpoint_expected.json
│   │       │   ├── golden-manifest.json
│   │       │   └── restore_expected.json
│   │       ├── failure-injection
│   │       │   ├── faulty_expected.json
│   │       │   └── golden-manifest.json
│   │       ├── hello-core
│   │       │   ├── checkpoint_header.json
│   │       │   ├── execution_certificate.json
│   │       │   ├── golden-identities.json
│   │       │   ├── golden-manifest.json
│   │       │   └── trace_snippet.json
│   │       ├── mini-tracking
│   │       │   └── expected.json
│   │       ├── perf-scale
│   │       │   ├── forward_expected.json
│   │       │   └── golden-manifest.json
│   │       ├── registry-lifecycle
│   │       │   ├── golden-manifest.json
│   │       │   ├── stage_transition_expected.json
│   │       │   └── version_create_expected.json
│   │       ├── replay-determinism
│   │       │   ├── golden-manifest.json
│   │       │   └── replay_expected.json
│   │       ├── replay-suite-1
│   │       │   ├── golden-manifest.json
│   │       │   └── trace_expected.json
│   │       ├── tracking-monitoring
│   │       │   ├── golden-manifest.json
│   │       │   └── metric_log_expected.json
│   │       └── golden_inventory.json
│   ├── generated
│   │   ├── build_metadata
│   │   │   ├── codegen_manifest.json
│   │   │   └── input_hashes.json
│   │   ├── codegen
│   │   │   ├── cleanroom_validation
│   │   │   │   ├── bindings.py
│   │   │   │   ├── error.py
│   │   │   │   ├── models.py
│   │   │   │   ├── operators.py
│   │   │   │   └── validators.py
│   │   │   ├── __init__.py
│   │   │   ├── bindings.py
│   │   │   ├── error.py
│   │   │   ├── models.py
│   │   │   ├── operators.py
│   │   │   └── validators.py
│   │   ├── deploy
│   │   │   ├── confidential
│   │   │   │   ├── bundle_manifest.json
│   │   │   │   ├── policy_bindings.json
│   │   │   │   └── runtime_config.json
│   │   │   ├── managed
│   │   │   │   ├── bundle_manifest.json
│   │   │   │   ├── policy_bindings.json
│   │   │   │   └── runtime_config.json
│   │   │   ├── overlays
│   │   │   │   ├── dev.json
│   │   │   │   ├── index.json
│   │   │   │   ├── prod.json
│   │   │   │   └── staging.json
│   │   │   ├── regulated
│   │   │   │   ├── bundle_manifest.json
│   │   │   │   ├── policy_bindings.json
│   │   │   │   └── runtime_config.json
│   │   │   ├── env_manifest.json
│   │   │   └── migration_plan.json
│   │   └── __init__.py
│   ├── inputs
│   │   ├── fixtures
│   │   │   ├── checkpoint-restore
│   │   │   │   ├── checkpoint_input.json
│   │   │   │   ├── fixture-manifest.json
│   │   │   │   └── restore_request.json
│   │   │   ├── failure-injection
│   │   │   │   ├── faulty_request.json
│   │   │   │   └── fixture-manifest.json
│   │   │   ├── hello-core
│   │   │   │   ├── checkpoint.json
│   │   │   │   ├── execution_certificate.json
│   │   │   │   ├── fixture-manifest.json
│   │   │   │   ├── manifest.core.yaml
│   │   │   │   ├── model_ir.json
│   │   │   │   ├── tiny_synth_dataset.jsonl
│   │   │   │   └── trace.json
│   │   │   ├── mini-tracking
│   │   │   │   └── inputs.json
│   │   │   ├── perf-scale
│   │   │   │   ├── batch.json
│   │   │   │   └── fixture-manifest.json
│   │   │   ├── registry-lifecycle
│   │   │   │   ├── fixture-manifest.json
│   │   │   │   ├── stage_transition.json
│   │   │   │   └── version_create.json
│   │   │   ├── replay-determinism
│   │   │   │   ├── fixture-manifest.json
│   │   │   │   └── trace.json
│   │   │   ├── replay-suite-1
│   │   │   │   ├── fixture-manifest.json
│   │   │   │   └── trace.json
│   │   │   └── tracking-monitoring
│   │   │       ├── fixture-manifest.json
│   │   │       └── run_event.json
│   │   └── vectors
│   │       ├── checkpoint-restore
│   │       │   ├── vectors-manifest.json
│   │       │   └── vectors.json
│   │       ├── conformance
│   │       │   ├── canonical_cbor
│   │       │   │   ├── .gitkeep
│   │       │   │   └── vectors.json
│   │       │   ├── interface_hash
│   │       │   │   ├── .gitkeep
│   │       │   │   └── vectors.json
│   │       │   ├── operators
│   │       │   │   ├── Glyphser_Backend_LoadDriver.json
│   │       │   │   ├── Glyphser_Certificate_EvidenceValidate.json
│   │       │   │   ├── Glyphser_Checkpoint_CheckpointMigrate.json
│   │       │   │   ├── Glyphser_Checkpoint_Restore.json
│   │       │   │   ├── Glyphser_Config_ManifestMigrate.json
│   │       │   │   ├── Glyphser_Data_NextBatch.json
│   │       │   │   ├── Glyphser_DifferentialPrivacy_Apply.json
│   │       │   │   ├── Glyphser_Error_Emit.json
│   │       │   │   ├── Glyphser_Import_LegacyFramework.json
│   │       │   │   ├── Glyphser_IO_SaveCheckpoint.json
│   │       │   │   ├── Glyphser_Model_Forward.json
│   │       │   │   ├── Glyphser_Model_ModelIR_Executor.json
│   │       │   │   ├── Glyphser_Monitor_DriftCompute.json
│   │       │   │   ├── Glyphser_Monitor_Emit.json
│   │       │   │   ├── Glyphser_Monitor_Register.json
│   │       │   │   ├── Glyphser_Registry_StageTransition.json
│   │       │   │   ├── Glyphser_Registry_VersionCreate.json
│   │       │   │   ├── Glyphser_TMMU_PrepareMemory.json
│   │       │   │   ├── Glyphser_Trace_TraceMigrate.json
│   │       │   │   ├── Glyphser_Tracking_ArtifactGet.json
│   │       │   │   ├── Glyphser_Tracking_ArtifactList.json
│   │       │   │   ├── Glyphser_Tracking_ArtifactPut.json
│   │       │   │   ├── Glyphser_Tracking_ArtifactTombstone.json
│   │       │   │   ├── Glyphser_Tracking_MetricLog.json
│   │       │   │   ├── Glyphser_Tracking_RunCreate.json
│   │       │   │   ├── Glyphser_Tracking_RunEnd.json
│   │       │   │   └── Glyphser_Tracking_RunStart.json
│   │       │   ├── storage
│   │       │   │   └── state_recovery_vectors.json
│   │       │   └── struct_validation
│   │       │       ├── .gitkeep
│   │       │       └── vectors.json
│   │       ├── failure-injection
│   │       │   ├── vectors-manifest.json
│   │       │   └── vectors.json
│   │       ├── hello-core
│   │       │   ├── vectors-manifest.json
│   │       │   └── vectors.json
│   │       ├── perf-scale
│   │       │   ├── vectors-manifest.json
│   │       │   └── vectors.json
│   │       ├── registry-lifecycle
│   │       │   ├── vectors-manifest.json
│   │       │   └── vectors.json
│   │       ├── replay-determinism
│   │       │   ├── vectors-manifest.json
│   │       │   └── vectors.json
│   │       ├── replay-suite-1
│   │       │   ├── vectors-manifest.json
│   │       │   └── vectors.json
│   │       ├── replay-suites
│   │       │   └── index.json
│   │       ├── tracking-monitoring
│   │       │   ├── vectors-manifest.json
│   │       │   └── vectors.json
│   │       └── catalog.json
│   ├── __init__.py
│   └── README.md
├── distribution
│   ├── release
│   │   ├── CHECKSUMS_v0.1.0.sha256
│   │   ├── CHECKSUMS_v0.1.0.sha256.asc
│   │   ├── RELEASE_NOTES_v0.1.0.md
│   │   ├── RELEASE_PUBKEY.asc
│   │   └── SIGNING.md
│   └── README.md
├── docs
│   ├── BRAND.md
│   ├── HELLO_CORE_NEXT_STEPS.md
│   ├── START-HERE.md
│   └── VERIFY.md
├── evidence
│   ├── conformance
│   │   ├── reports
│   │   │   └── latest.json
│   │   └── results
│   │       └── latest.json
│   ├── coverage
│   │   └── operator_coverage.json
│   ├── deploy
│   │   ├── state
│   │   │   ├── staging_active.json
│   │   │   └── staging_previous.json
│   │   ├── drift.json
│   │   ├── latest.json
│   │   ├── parity.json
│   │   └── rollback.json
│   ├── ga
│   │   ├── latest.json
│   │   └── release_candidate_verification.json
│   ├── observability
│   │   ├── alert_test.json
│   │   ├── dashboard_inventory.json
│   │   ├── incident_drill.json
│   │   ├── latest.json
│   │   ├── lineage_index.json
│   │   ├── slo_status.json
│   │   └── synthetic_probe.json
│   ├── recovery
│   │   ├── backup-restore-drill.json
│   │   ├── checkpoint-backup.json
│   │   ├── latest.json
│   │   └── replay-proof.txt
│   ├── repro
│   │   ├── compare-20260228.md
│   │   ├── compare-template.md
│   │   ├── dependency-lock.sha256
│   │   ├── hashes.txt
│   │   └── run-checklist.md
│   ├── runtime_state
│   │   ├── checkpoint-restore
│   │   │   └── ckpt-1.json
│   │   └── deploy
│   │       ├── staging_active.json
│   │       └── staging_previous.json
│   ├── security
│   │   ├── audit.log.jsonl
│   │   ├── build_provenance.json
│   │   ├── latest.json
│   │   └── sbom.json
│   ├── structure
│   │   ├── domain_dependency_gate.json
│   │   ├── latest.json
│   │   ├── legacy_path_gate.json
│   │   ├── PROJECT_FILE_INVENTORY.md
│   │   ├── spec_link_gate.json
│   │   ├── spec_schema_map.json
│   │   └── structural_invariants.json
│   ├── validation
│   │   ├── runs
│   │   │   ├── run-01-linux-mint.json
│   │   │   ├── run-02-ubuntu-wsl.json
│   │   │   └── run-03-docs-only-cleanroom.json
│   │   ├── scorecards
│   │   │   ├── run-01-linux-mint.json
│   │   │   ├── run-02-ubuntu-wsl.json
│   │   │   └── run-03-docs-only-cleanroom.json
│   │   ├── transcripts
│   │   │   ├── run-01-linux-mint.md
│   │   │   ├── run-02-ubuntu-wsl.md
│   │   │   └── run-03-docs-only-cleanroom.md
│   │   ├── external_security_review.md
│   │   ├── independent_verification_summary.json
│   │   ├── issues.json
│   │   └── latest.json
│   └── README.md
├── governance
│   ├── document_guidelines
│   │   └── EquationCode
│   │       ├── BRIDGE.md
│   │       ├── ECOSYSTEM.md
│   │       ├── EQC.md
│   │       ├── LICENSE
│   │       └── README.md
│   ├── ecosystem
│   │   ├── ecosystem-compatibility-aggregate.yaml
│   │   ├── ecosystem-graph.yaml
│   │   ├── ecosystem-registry.yaml
│   │   ├── ecosystem-validation-log.md
│   │   ├── ecosystem.md
│   │   └── tooling-manifest.yaml
│   ├── ip
│   │   ├── BADGE_PROGRAM_DRAFT.md
│   │   ├── DEFENSIVE_PUBLICATION_PLAN.md
│   │   ├── DISCLOSURE-RULES.md
│   │   └── IP-POSTURE.md
│   ├── lint
│   │   ├── semantic_lint_high_confidence.txt
│   │   └── semantic_lint_report.txt
│   ├── process
│   │   ├── Community-Governance-Model.md
│   │   ├── Contributing-Workflow.md
│   │   └── PR-Review-Checklist.md
│   ├── registry
│   │   └── data-registry.yaml
│   ├── roadmap
│   │   ├── INTERPRETATION_LOG.md
│   │   ├── migration-plan-template.yaml
│   │   ├── milestones.txt
│   │   └── WEEKLY_REVIEW_TEMPLATE.md
│   ├── security
│   │   ├── OPERATIONS.md
│   │   └── THREAT_MODEL.md
│   ├── structure
│   │   ├── templates
│   │   │   └── PROJECT_FILE_INVENTORY_TEMPLATE.md
│   │   ├── CANONICAL_CBOR_VECTORS_README.md
│   │   ├── DOC_CODE_SEPARATION_POLICY.md
│   │   ├── DOCUMENT_AUDIENCE_POLICY.md
│   │   ├── OPERATOR_STUB_VECTORS_README.txt
│   │   ├── PHASE1_RESTRUCTURE_MAP.md
│   │   ├── PHASE2_ARTIFACT_CONSOLIDATION.md
│   │   ├── PROJECT_FILE_INVENTORY.md
│   │   ├── spec_link_policy.json
│   │   ├── spec_schema_map.json
│   │   └── STRUCTURAL_INVARIANTS.md
│   └── README.md
├── product
│   ├── business
│   │   ├── DELIVERABLES_LIST.md
│   │   ├── FEES.md
│   │   ├── LOCAL_NETWORK.md
│   │   ├── OFFERS.md
│   │   └── STRUCTURE_TRACK.md
│   ├── docs
│   │   ├── how_to
│   │   │   └── MILESTONE_15_TWO_HOST_RUNBOOK.md
│   │   ├── reports
│   │   │   ├── CONFORMANCE_REPORT_TEMPLATE.md
│   │   │   ├── INTEGRATION_REPORT_TEMPLATE.md
│   │   │   ├── merged_docs.txt
│   │   │   └── OUTREACH_2026-02-27.md
│   │   ├── ACCESSIBILITY_REVIEW.md
│   │   ├── ANNUAL_SECURITY_REVIEW_POLICY.md
│   │   ├── API_CLI_COMMANDS.md
│   │   ├── API_LIFECYCLE_POLICY.md
│   │   ├── API_REFERENCE_v1.md
│   │   ├── API_STYLE_GUIDE.md
│   │   ├── CHANGE_COMMUNICATION_SLA.md
│   │   ├── COMPLIANCE_EVIDENCE_INDEX.md
│   │   ├── DEPENDENCY_LICENSE_REVIEW.md
│   │   ├── DOCS_VERSIONING_POLICY.md
│   │   ├── GA_COMPATIBILITY_GUARANTEES.md
│   │   ├── GA_CONTRACTUAL_SUPPORT_SLA.md
│   │   ├── GA_GO_NO_GO_CHECKLIST.md
│   │   ├── GA_MIGRATION_GUIDE.md
│   │   ├── GA_RELEASE_TRAIN_POLICY.md
│   │   ├── GA_SIGNOFF.md
│   │   ├── GA_STATUS_INCIDENT_COMMUNICATION.md
│   │   ├── GA_SUPPORT_LIFECYCLE.md
│   │   ├── GA_SUPPORT_MATRIX.md
│   │   ├── GA_SUPPORT_OPERATIONS_READINESS.md
│   │   ├── M17_APPROVAL.md
│   │   ├── M18_CONTRACT_TEST_REPORT.md
│   │   ├── M19_RECOVERY_TEST_REPORT.md
│   │   ├── M20_SECURITY_TEST_REPORT.md
│   │   ├── M21_DEPLOYMENT_TEST_REPORT.md
│   │   ├── M22_OBSERVABILITY_REPORT.md
│   │   ├── M23_EXTERNAL_VALIDATION_REPORT.md
│   │   ├── M24_GA_RELEASE_REPORT.md
│   │   ├── PERSISTENCE_SCHEMA_v1.md
│   │   ├── PERSISTENT_STORAGE_ADAPTER_CONTRACT.md
│   │   ├── portfolio-release-notes-template.md
│   │   ├── POST_GA_GOVERNANCE.md
│   │   ├── PRIVACY_IMPACT_ASSESSMENT_WORKFLOW.md
│   │   ├── PRODUCT_SCOPE.md
│   │   ├── RUNTIME_PROFILES.md
│   │   └── SUPPLY_CHAIN_TRUST_POLICY.md
│   ├── ops
│   │   ├── DEPLOYMENT_RUNBOOK.md
│   │   ├── INCIDENT_RESPONSE.md
│   │   ├── ROLLBACK_RUNBOOK.md
│   │   └── SLOs.md
│   ├── site
│   │   ├── assets
│   │   │   ├── glyphser3.png
│   │   │   └── glyphser3.svg
│   │   ├── services.md
│   │   └── verify.md
│   └── README.md
├── specs
│   ├── compatibility
│   │   ├── CERTIFICATION_DELIVERABLES.md
│   │   ├── COMPATIBILITY_CRITERIA_v0.1.md
│   │   └── VENDOR_SELF_TEST_KIT.md
│   ├── contracts
│   │   ├── capability_catalog.cbor
│   │   ├── catalog-manifest.json
│   │   ├── digest_catalog.cbor
│   │   ├── error_codes.cbor
│   │   ├── error_codes.json
│   │   ├── interface_hash.json
│   │   ├── openapi_public_api_v1.yaml
│   │   ├── operator_registry.cbor
│   │   ├── operator_registry.json
│   │   ├── operator_registry_source.json
│   │   ├── schema_catalog.cbor
│   │   └── vectors_catalog.cbor
│   ├── examples
│   │   ├── hello-core
│   │   │   ├── hello-core-golden.json
│   │   │   └── manifest.core.yaml
│   │   └── operators
│   │       ├── Glyphser_IO_SaveCheckpoint.json
│   │       ├── Glyphser_Model_Forward.json
│   │       └── README.md
│   ├── layers
│   │   ├── L1-foundation
│   │   │   ├── API-Interfaces.md
│   │   │   ├── Canonical-CBOR-Profile.md
│   │   │   ├── Data-Structures.md
│   │   │   ├── Dependency-Lock-Policy.md
│   │   │   ├── Determinism-Profiles.md
│   │   │   ├── Digest-Catalog.md
│   │   │   ├── Environment-Manifest.md
│   │   │   ├── Error-Codes.md
│   │   │   ├── Normativity-Legend.md
│   │   │   ├── Operator-Registry-Schema.md
│   │   │   ├── README.md
│   │   │   └── Redaction-Policy.md
│   │   ├── L2-specs
│   │   │   ├── AuthZ-Capability-Matrix.md
│   │   │   ├── Checkpoint-Schema.md
│   │   │   ├── Config-Schema.md
│   │   │   ├── Data-Lineage.md
│   │   │   ├── Data-NextBatch.md
│   │   │   ├── Deployment-Runbook.md
│   │   │   ├── DifferentialPrivacy-Apply.md
│   │   │   ├── Evaluation-Harness.md
│   │   │   ├── Execution-Certificate.md
│   │   │   ├── Experiment-Tracking.md
│   │   │   ├── Glyphser-Kernel-v3.22-OS.md
│   │   │   ├── Model-Registry.md
│   │   │   ├── ModelIR-Executor.md
│   │   │   ├── Monitoring-Policy.md
│   │   │   ├── Pipeline-Orchestrator.md
│   │   │   ├── README.md
│   │   │   ├── Replay-Determinism.md
│   │   │   ├── Run-Commit-WAL.md
│   │   │   ├── Security-Compliance-Profile.md
│   │   │   ├── TMMU-Allocation.md
│   │   │   └── Trace-Sidecar.md
│   │   ├── L3-tests
│   │   │   ├── Compatibility-Test-Matrix.md
│   │   │   ├── Conformance-CI-Pipeline.md
│   │   │   ├── Conformance-Harness-Guide.md
│   │   │   ├── Coverage-Targets.md
│   │   │   ├── Data-Contract-Fuzzing-Guide.md
│   │   │   ├── Failure-Injection-Index.md
│   │   │   ├── Failure-Injection-Scenarios.md
│   │   │   ├── Game-Day-Scenarios.md
│   │   │   ├── Integration-Test-Matrix.md
│   │   │   ├── Operator-Vectors.md
│   │   │   ├── Performance-Plan.md
│   │   │   ├── README.md
│   │   │   ├── Release-Gates.md
│   │   │   ├── Storage-Recovery-Test-Matrix.md
│   │   │   ├── Test-Coverage-Gaps.md
│   │   │   ├── Test-Inventory.md
│   │   │   ├── Test-Plan.md
│   │   │   └── Test-Vectors-Catalog.md
│   │   └── L4-implementation
│   │       ├── Algorithm-Closure.md
│   │       ├── API-Lifecycle-and-Deprecation-Policy.md
│   │       ├── Architecture-Decisions-Log.md
│   │       ├── Artifact-Store-Adapter-Guide.md
│   │       ├── Backend-Adapter-Guide.md
│   │       ├── Backend-Feature-Matrix.md
│   │       ├── Benchmark-Evidence-Spec.md
│   │       ├── Brownfield-Deployment-Guide.md
│   │       ├── Build-and-CI-Matrix.md
│   │       ├── Canonical-Hashing-Reference.md
│   │       ├── Change-Control-Playbook.md
│   │       ├── CLI-Command-Profiles.md
│   │       ├── Code-Generation-Mapping.md
│   │       ├── Coding-Standards.md
│   │       ├── Command-Reference.md
│   │       ├── Common-Pitfalls-Guide.md
│   │       ├── Contracts-Artifact-Lifecycle.md
│   │       ├── Debugging-Playbook.md
│   │       ├── Deployment-Generation-Profile.md
│   │       ├── Determinism-Audit-Playbook.md
│   │       ├── Determinism-Debug-Checklist.md
│   │       ├── Deterministic-RNG-Implementation-Guide.md
│   │       ├── Developer-Setup.md
│   │       ├── Developer-Troubleshooting-FAQ.md
│   │       ├── Disaster-Recovery-Operations-Runbook.md
│   │       ├── Distributed-Failure-Recovery-Guide.md
│   │       ├── Ecosystem-Expansion-Roadmap.md
│   │       ├── EQC-CI-Policy.md
│   │       ├── Evidence-Catalog.md
│   │       ├── Expansion-Catalog-041-250.md
│   │       ├── External-Interface-Standard.md
│   │       ├── Fixtures-and-Golden-Data.md
│   │       ├── Formal-Verification-Roadmap.md
│   │       ├── Gentle-Introduction.md
│   │       ├── Hello-World-End-to-End-Example.md
│   │       ├── Implementation-Backlog.md
│   │       ├── Implementation-Roadmap.md
│   │       ├── Incident-Postmortem-Template.md
│   │       ├── Industry-Productization-Upgrade-Plan.md
│   │       ├── Interoperability-Standards-Bridge.md
│   │       ├── Local-Replay-Runbook.md
│   │       ├── Migration-Execution-Guide.md
│   │       ├── Module-Scaffolding-Guide.md
│   │       ├── Operator-Conformance-Matrix.md
│   │       ├── Operator-Readiness-Checklist.md
│   │       ├── Operator-Registry-CBOR-Contract.md
│   │       ├── Operator-SDK-Scaffold-Template.md
│   │       ├── Profiling-and-Optimization-Guide.md
│   │       ├── README.md
│   │       ├── Reference-Implementations.md
│   │       ├── Reference-Stack-Minimal.md
│   │       ├── Release-Evidence-Assembler.md
│   │       ├── Repo-Layout-and-Interfaces.md
│   │       ├── Research-Extensions-Roadmap.md
│   │       ├── Runtime-State-Machine-Reference.md
│   │       ├── Schema-Evolution-Playbook.md
│   │       ├── Scope-and-Non-Goals.md
│   │       ├── SDK-Usage-Guide.md
│   │       ├── Security-Case-Template.md
│   │       ├── Security-Coding-Checklist.md
│   │       ├── Spec-Lint-Implementation.md
│   │       ├── Spec-Lint-Rules.md
│   │       ├── SRE-Incident-Triage-Playbook.md
│   │       ├── Target-Architecture-Profile.md
│   │       ├── Test-Harness-Implementation.md
│   │       ├── Third-Party-Operator-Certification-Program.md
│   │       ├── Threat-Model-and-Control-Crosswalk.md
│   │       ├── Tooling-and-Automation-Suite.md
│   │       └── Tooling-Suite.md
│   ├── policies
│   │   ├── COMPATIBILITY_POLICY.md
│   │   ├── CONFORMANCE_SUITE_v0.1.md
│   │   ├── DETERMINISM_PROFILE_v0.1.md
│   │   ├── ERROR_CODES.md
│   │   └── NUMERIC_POLICY_v0.1.md
│   ├── schemas
│   │   ├── layers
│   │   │   ├── L1
│   │   │   │   ├── l1_api_interfaces.schema.json
│   │   │   │   ├── l1_canonical_cbor_profile.schema.json
│   │   │   │   ├── l1_data_structures.schema.json
│   │   │   │   ├── l1_dependency_lock_policy.schema.json
│   │   │   │   ├── l1_determinism_profiles.schema.json
│   │   │   │   ├── l1_digest_catalog.schema.json
│   │   │   │   ├── l1_environment_manifest.schema.json
│   │   │   │   ├── l1_error_codes.schema.json
│   │   │   │   ├── l1_normativity_legend.schema.json
│   │   │   │   ├── l1_operator_registry_schema.schema.json
│   │   │   │   ├── l1_redaction_policy.schema.json
│   │   │   │   └── README.md
│   │   │   ├── L2
│   │   │   │   ├── l2_authz-capability-matrix.schema.json
│   │   │   │   ├── l2_checkpoint-schema.schema.json
│   │   │   │   ├── l2_config-schema.schema.json
│   │   │   │   ├── l2_data-lineage.schema.json
│   │   │   │   ├── l2_data-nextbatch.schema.json
│   │   │   │   ├── l2_deployment-runbook.schema.json
│   │   │   │   ├── l2_differentialprivacy-apply.schema.json
│   │   │   │   ├── l2_evaluation-harness.schema.json
│   │   │   │   ├── l2_execution-certificate.schema.json
│   │   │   │   ├── l2_experiment-tracking.schema.json
│   │   │   │   ├── l2_glyphser-kernel-v3.22-os.schema.json
│   │   │   │   ├── l2_model-registry.schema.json
│   │   │   │   ├── l2_modelir-executor.schema.json
│   │   │   │   ├── l2_monitoring-policy.schema.json
│   │   │   │   ├── l2_pipeline-orchestrator.schema.json
│   │   │   │   ├── l2_replay-determinism.schema.json
│   │   │   │   ├── l2_run-commit-wal.schema.json
│   │   │   │   ├── l2_security-compliance-profile.schema.json
│   │   │   │   ├── l2_tmmu-allocation.schema.json
│   │   │   │   ├── l2_trace-sidecar.schema.json
│   │   │   │   └── README.md
│   │   │   ├── L3
│   │   │   │   ├── l3_compatibility-test-matrix.schema.json
│   │   │   │   ├── l3_conformance-ci-pipeline.schema.json
│   │   │   │   ├── l3_conformance-harness-guide.schema.json
│   │   │   │   ├── l3_coverage-targets.schema.json
│   │   │   │   ├── l3_data-contract-fuzzing-guide.schema.json
│   │   │   │   ├── l3_failure-injection-index.schema.json
│   │   │   │   ├── l3_failure-injection-scenarios.schema.json
│   │   │   │   ├── l3_game-day-scenarios.schema.json
│   │   │   │   ├── l3_integration-test-matrix.schema.json
│   │   │   │   ├── l3_operator_error_vectors.schema.json
│   │   │   │   ├── l3_operator_vectors.schema.json
│   │   │   │   ├── l3_performance-plan.schema.json
│   │   │   │   ├── l3_release-gates.schema.json
│   │   │   │   ├── l3_storage-recovery-test-matrix.schema.json
│   │   │   │   ├── l3_test-plan.schema.json
│   │   │   │   ├── l3_test-vectors-catalog.schema.json
│   │   │   │   └── README.md
│   │   │   └── L4
│   │   │       ├── l4_api-lifecycle-and-deprecation-policy.schema.json
│   │   │       ├── l4_architecture-decisions-log.schema.json
│   │   │       ├── l4_artifact-store-adapter-guide.schema.json
│   │   │       ├── l4_backend-adapter-guide.schema.json
│   │   │       ├── l4_backend-feature-matrix.schema.json
│   │   │       ├── l4_benchmark-evidence-spec.schema.json
│   │   │       ├── l4_brownfield-deployment-guide.schema.json
│   │   │       ├── l4_build-and-ci-matrix.schema.json
│   │   │       ├── l4_canonical-hashing-reference.schema.json
│   │   │       ├── l4_change-control-playbook.schema.json
│   │   │       ├── l4_cli-command-profiles.schema.json
│   │   │       ├── l4_code-generation-mapping.schema.json
│   │   │       ├── l4_coding-standards.schema.json
│   │   │       ├── l4_command-reference.schema.json
│   │   │       ├── l4_common-pitfalls-guide.schema.json
│   │   │       ├── l4_community-governance-model.schema.json
│   │   │       ├── l4_contracts-artifact-lifecycle.schema.json
│   │   │       ├── l4_contributing-workflow.schema.json
│   │   │       ├── l4_debugging-playbook.schema.json
│   │   │       ├── l4_determinism-audit-playbook.schema.json
│   │   │       ├── l4_determinism-debug-checklist.schema.json
│   │   │       ├── l4_deterministic-rng-implementation-guide.schema.json
│   │   │       ├── l4_developer-setup.schema.json
│   │   │       ├── l4_developer-troubleshooting-faq.schema.json
│   │   │       ├── l4_disaster-recovery-operations-runbook.schema.json
│   │   │       ├── l4_distributed-failure-recovery-guide.schema.json
│   │   │       ├── l4_ecosystem-expansion-roadmap.schema.json
│   │   │       ├── l4_eqc-ci-policy.schema.json
│   │   │       ├── l4_evidence-catalog.schema.json
│   │   │       ├── l4_expansion-catalog-041-250.schema.json
│   │   │       ├── l4_external-interface-standard.schema.json
│   │   │       ├── l4_fixtures-and-golden-data.schema.json
│   │   │       ├── l4_formal-verification-roadmap.schema.json
│   │   │       ├── l4_gentle-introduction.schema.json
│   │   │       ├── l4_hello-world-end-to-end-example.schema.json
│   │   │       ├── l4_implementation-backlog.schema.json
│   │   │       ├── l4_implementation-roadmap.schema.json
│   │   │       ├── l4_incident-postmortem-template.schema.json
│   │   │       ├── l4_industry-productization-upgrade-plan.schema.json
│   │   │       ├── l4_interoperability-standards-bridge.schema.json
│   │   │       ├── l4_local-replay-runbook.schema.json
│   │   │       ├── l4_migration-execution-guide.schema.json
│   │   │       ├── l4_module-scaffolding-guide.schema.json
│   │   │       ├── l4_operator-conformance-matrix.schema.json
│   │   │       ├── l4_operator-registry-cbor-contract.schema.json
│   │   │       ├── l4_operator-sdk-scaffold-template.schema.json
│   │   │       ├── l4_pr-review-checklist.schema.json
│   │   │       ├── l4_profiling-and-optimization-guide.schema.json
│   │   │       ├── l4_reference-implementations.schema.json
│   │   │       ├── l4_reference-stack-minimal.schema.json
│   │   │       ├── l4_release-evidence-assembler.schema.json
│   │   │       ├── l4_repo-layout-and-interfaces.schema.json
│   │   │       ├── l4_research-extensions-roadmap.schema.json
│   │   │       ├── l4_runtime-state-machine-reference.schema.json
│   │   │       ├── l4_schema-evolution-playbook.schema.json
│   │   │       ├── l4_scope-and-non-goals.schema.json
│   │   │       ├── l4_sdk-usage-guide.schema.json
│   │   │       ├── l4_security-case-template.schema.json
│   │   │       ├── l4_security-coding-checklist.schema.json
│   │   │       ├── l4_spec-lint-implementation.schema.json
│   │   │       ├── l4_spec-lint-rules.schema.json
│   │   │       ├── l4_sre-incident-triage-playbook.schema.json
│   │   │       ├── l4_test-harness-implementation.schema.json
│   │   │       ├── l4_third-party-operator-certification-program.schema.json
│   │   │       ├── l4_threat-model-and-control-crosswalk.schema.json
│   │   │       ├── l4_tooling-and-automation-suite.schema.json
│   │   │       ├── l4_tooling-suite.schema.json
│   │   │       └── README.md
│   │   ├── contract_schema_meta.json
│   │   ├── README.md
│   │   ├── SCHEMA_CONVENTIONS.txt
│   │   └── SCHEMA_FORMAT_DECISION.txt
│   └── README.md
├── src
│   └── glyphser
│       ├── api
│       │   ├── runtime_api.py
│       │   └── validate_signature.py
│       ├── backend
│       │   ├── load_driver.py
│       │   └── reference_driver.py
│       ├── cert
│       │   └── evidence_validate.py
│       ├── certificate
│       │   └── build.py
│       ├── checkpoint
│       │   ├── migrate_checkpoint.py
│       │   ├── restore.py
│       │   └── write.py
│       ├── config
│       │   └── migrate_manifest.py
│       ├── contract
│       │   └── validate.py
│       ├── data
│       │   └── next_batch.py
│       ├── data_structures
│       │   └── validate_struct.py
│       ├── dp
│       │   └── apply.py
│       ├── error
│       │   └── emit.py
│       ├── fingerprint
│       │   └── state_fingerprint.py
│       ├── legacy_import
│       │   └── legacy_framework.py
│       ├── model
│       │   ├── build_grad_dependency_order.py
│       │   ├── collect_gradients.py
│       │   ├── dispatch_primitive.py
│       │   ├── forward.py
│       │   ├── ir_schema.py
│       │   ├── model_ir_executor.py
│       │   └── topo_sort_nodes.py
│       ├── monitor
│       │   ├── drift_compute.py
│       │   ├── emit.py
│       │   └── register.py
│       ├── registry
│       │   ├── interface_hash.py
│       │   ├── registry_builder.py
│       │   ├── stage_transition.py
│       │   └── version_create.py
│       ├── security
│       │   ├── __init__.py
│       │   ├── audit.py
│       │   └── authz.py
│       ├── serialization
│       │   └── canonical_cbor.py
│       ├── storage
│       │   ├── __init__.py
│       │   └── state_store.py
│       ├── tmmu
│       │   ├── commit_execution.py
│       │   └── prepare_memory.py
│       ├── trace
│       │   ├── compute_trace_hash.py
│       │   ├── migrate_trace.py
│       │   └── trace_sidecar.py
│       └── tracking
│           ├── artifact_get.py
│           ├── artifact_list.py
│           ├── artifact_put.py
│           ├── artifact_tombstone.py
│           ├── metric_log.py
│           ├── run_create.py
│           ├── run_end.py
│           └── run_start.py
├── tests
│   ├── api
│   │   ├── __init__.py
│   │   ├── test_api_cli.py
│   │   ├── test_api_contract_gate.py
│   │   ├── test_runtime_api.py
│   │   └── test_validate_signature.py
│   ├── canonical_cbor
│   │   ├── __init__.py
│   │   ├── test_fuzz.py
│   │   ├── test_vectors.py
│   │   └── vector_loader.py
│   ├── chaos
│   │   └── test_distributed_chaos.py
│   ├── data_structures
│   │   ├── __init__.py
│   │   ├── test_validate_struct.py
│   │   └── test_vectors.py
│   ├── deploy
│   │   └── test_deploy_pipeline_gate.py
│   ├── fixtures
│   │   └── test_mini_tracking_fixture.py
│   ├── fuzz
│   │   ├── test_checkpoint_decode_fuzz.py
│   │   ├── test_ir_validation_fuzz.py
│   │   ├── test_manifest_parser_fuzz.py
│   │   ├── test_schema_parsing_fuzz.py
│   │   ├── test_tmmu_planner_invariants.py
│   │   └── test_trace_parser_fuzz.py
│   ├── ga
│   │   └── test_ga_release_gate.py
│   ├── goldens
│   │   └── test_golden_inventory.py
│   ├── interface_hash
│   │   ├── __init__.py
│   │   └── test_vectors.py
│   ├── operators
│   │   ├── __init__.py
│   │   ├── test_glyphser_backend_stubs.py
│   │   ├── test_glyphser_certificate_stubs.py
│   │   ├── test_glyphser_checkpoint_stubs.py
│   │   ├── test_glyphser_config_stubs.py
│   │   ├── test_glyphser_data_stubs.py
│   │   ├── test_glyphser_differentialprivacy_stubs.py
│   │   ├── test_glyphser_error_stubs.py
│   │   ├── test_glyphser_import_stubs.py
│   │   ├── test_glyphser_io_stubs.py
│   │   ├── test_glyphser_model_stubs.py
│   │   ├── test_glyphser_monitor_stubs.py
│   │   ├── test_glyphser_registry_stubs.py
│   │   ├── test_glyphser_tmmu_stubs.py
│   │   ├── test_glyphser_trace_stubs.py
│   │   └── test_glyphser_tracking_stubs.py
│   ├── ops
│   │   ├── test_doc_code_separation_gate.py
│   │   ├── test_domain_dependency_gate.py
│   │   ├── test_legacy_path_gate.py
│   │   ├── test_observability_gate.py
│   │   ├── test_spec_link_gate.py
│   │   ├── test_spec_schema_map_gate.py
│   │   └── test_structural_invariants_gate.py
│   ├── replay
│   │   ├── test_determinism_regression_matrix.py
│   │   └── test_replay_divergence.py
│   ├── security
│   │   ├── test_authz_and_audit.py
│   │   └── test_security_baseline_gate.py
│   ├── storage
│   │   └── test_state_store_recovery.py
│   ├── trace
│   │   ├── __init__.py
│   │   └── test_compute_trace_hash.py
│   ├── validation
│   │   └── test_external_validation_gate.py
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_determinism_repeat.py
│   ├── test_error_codes_manifest.py
│   ├── test_error_emit.py
│   ├── test_operator_vectors.py
│   ├── test_replay_binding.py
│   ├── test_replay_suite.py
│   └── test_smoke.py
├── tooling
│   ├── cli
│   │   ├── __init__.py
│   │   ├── api_cli.py
│   │   └── conformance_cli.py
│   ├── codegen
│   │   ├── templates
│   │   │   ├── bindings.py.tpl
│   │   │   ├── error.py.tpl
│   │   │   ├── models.py.tpl
│   │   │   ├── operators.py.tpl
│   │   │   └── validators.py.tpl
│   │   ├── __init__.py
│   │   ├── check_generated_drift.py
│   │   ├── cleanroom_validation.py
│   │   ├── cleanroom_validation_generate.py
│   │   ├── diff_fidelity.py
│   │   ├── generate.py
│   │   ├── input_hash_manifest.py
│   │   └── run_and_test.py
│   ├── conformance
│   │   ├── __init__.py
│   │   ├── cli.py
│   │   └── report_template.json
│   ├── deploy
│   │   ├── overlay_templates
│   │   │   ├── dev.json
│   │   │   ├── prod.json
│   │   │   └── staging.json
│   │   ├── templates
│   │   │   ├── policy_bindings.json.tpl
│   │   │   └── runtime_config.json.tpl
│   │   ├── __init__.py
│   │   ├── deploy_rollback_gate.py
│   │   ├── generate_bundle.py
│   │   ├── generate_env_manifest.py
│   │   ├── generate_migration_plan.py
│   │   ├── generate_overlays.py
│   │   ├── run_deployment_pipeline.py
│   │   └── validate_profile.py
│   ├── docs
│   │   ├── __init__.py
│   │   ├── materialize_doc_artifacts.py
│   │   ├── merge_markdown_to_txt.py
│   │   └── verify_doc_artifacts.py
│   ├── gates
│   │   ├── __init__.py
│   │   ├── api_contract_gate.py
│   │   ├── coverage_report.py
│   │   ├── doc_code_separation_gate.py
│   │   ├── domain_dependency_gate.py
│   │   ├── error_code_gate.py
│   │   ├── external_validation_gate.py
│   │   ├── fixtures_gate.py
│   │   ├── legacy_path_gate.py
│   │   ├── observability_gate.py
│   │   ├── registry_gate.py
│   │   ├── schema_gate.py
│   │   ├── spec_link_gate.py
│   │   ├── spec_lint.py
│   │   ├── spec_schema_map_gate.py
│   │   ├── state_recovery_gate.py
│   │   ├── structural_invariants_gate.py
│   │   └── vector_gate.py
│   ├── registry
│   │   ├── __init__.py
│   │   ├── build_operator_registry.py
│   │   └── operator_vectors.py
│   ├── release
│   │   ├── __init__.py
│   │   ├── build_release_bundle.py
│   │   ├── ga_release_gate.py
│   │   ├── release_evidence_gate.py
│   │   ├── reproducibility_check.py
│   │   └── verify_release.py
│   ├── scripts
│   │   ├── repro
│   │   │   └── host_meta.py
│   │   └── run_hello_core.py
│   ├── security
│   │   ├── __init__.py
│   │   ├── security_artifacts.py
│   │   └── security_baseline_gate.py
│   ├── validation
│   │   ├── __init__.py
│   │   ├── generate_project_inventory.py
│   │   └── validate_data_integrity.py
│   ├── __init__.py
│   ├── path_config.py
│   ├── push_button.py
│   └── README.md
├── .gitignore
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── Dockerfile
├── LICENSE
├── pyproject.toml
├── README.md
├── requirements.lock
├── SECURITY.md
└── VERSIONING.md
```

## File Purpose Index
| File | Purpose |
|---|---|
| `.github/workflows/conformance-gate.yml` | CI/CD workflow automation configuration. |
| `.github/workflows/push-button.yml` | CI/CD workflow automation configuration. |
| `.github/workflows/registry-gate.yml` | CI/CD workflow automation configuration. |
| `.github/workflows/schema-gate.yml` | CI/CD workflow automation configuration. |
| `.gitignore` | Repository-level configuration or supporting documentation. |
| `CODE_OF_CONDUCT.md` | Repository-level configuration or supporting documentation. |
| `CONTRIBUTING.md` | Repository-level configuration or supporting documentation. |
| `Dockerfile` | Repository-level configuration or supporting documentation. |
| `LICENSE` | Repository-level configuration or supporting documentation. |
| `README.md` | Repository-level configuration or supporting documentation. |
| `SECURITY.md` | Repository-level configuration or supporting documentation. |
| `VERSIONING.md` | Repository-level configuration or supporting documentation. |
| `artifacts/README.md` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/__init__.py` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/bundles/hello-core-bundle.sha256` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/bundles/hello-core-bundle.tar.gz` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/expected/goldens/checkpoint-restore/checkpoint_expected.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/expected/goldens/checkpoint-restore/golden-manifest.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/expected/goldens/checkpoint-restore/restore_expected.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/expected/goldens/failure-injection/faulty_expected.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/expected/goldens/failure-injection/golden-manifest.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/expected/goldens/golden_inventory.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/expected/goldens/hello-core/checkpoint_header.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/expected/goldens/hello-core/execution_certificate.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/expected/goldens/hello-core/golden-identities.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/expected/goldens/hello-core/golden-manifest.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/expected/goldens/hello-core/trace_snippet.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/expected/goldens/mini-tracking/expected.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/expected/goldens/perf-scale/forward_expected.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/expected/goldens/perf-scale/golden-manifest.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/expected/goldens/registry-lifecycle/golden-manifest.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/expected/goldens/registry-lifecycle/stage_transition_expected.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/expected/goldens/registry-lifecycle/version_create_expected.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/expected/goldens/replay-determinism/golden-manifest.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/expected/goldens/replay-determinism/replay_expected.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/expected/goldens/replay-suite-1/golden-manifest.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/expected/goldens/replay-suite-1/trace_expected.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/expected/goldens/tracking-monitoring/golden-manifest.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/expected/goldens/tracking-monitoring/metric_log_expected.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/generated/__init__.py` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/generated/build_metadata/codegen_manifest.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/generated/build_metadata/input_hashes.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/generated/codegen/__init__.py` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/generated/codegen/bindings.py` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/generated/codegen/cleanroom_validation/bindings.py` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/generated/codegen/cleanroom_validation/error.py` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/generated/codegen/cleanroom_validation/models.py` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/generated/codegen/cleanroom_validation/operators.py` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/generated/codegen/cleanroom_validation/validators.py` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/generated/codegen/error.py` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/generated/codegen/models.py` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/generated/codegen/operators.py` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/generated/codegen/validators.py` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/generated/deploy/confidential/bundle_manifest.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/generated/deploy/confidential/policy_bindings.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/generated/deploy/confidential/runtime_config.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/generated/deploy/env_manifest.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/generated/deploy/managed/bundle_manifest.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/generated/deploy/managed/policy_bindings.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/generated/deploy/managed/runtime_config.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/generated/deploy/migration_plan.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/generated/deploy/overlays/dev.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/generated/deploy/overlays/index.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/generated/deploy/overlays/prod.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/generated/deploy/overlays/staging.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/generated/deploy/regulated/bundle_manifest.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/generated/deploy/regulated/policy_bindings.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/generated/deploy/regulated/runtime_config.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/fixtures/checkpoint-restore/checkpoint_input.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/fixtures/checkpoint-restore/fixture-manifest.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/fixtures/checkpoint-restore/restore_request.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/fixtures/failure-injection/faulty_request.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/fixtures/failure-injection/fixture-manifest.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/fixtures/hello-core/checkpoint.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/fixtures/hello-core/execution_certificate.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/fixtures/hello-core/fixture-manifest.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/fixtures/hello-core/manifest.core.yaml` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/fixtures/hello-core/model_ir.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/fixtures/hello-core/tiny_synth_dataset.jsonl` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/fixtures/hello-core/trace.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/fixtures/mini-tracking/inputs.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/fixtures/perf-scale/batch.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/fixtures/perf-scale/fixture-manifest.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/fixtures/registry-lifecycle/fixture-manifest.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/fixtures/registry-lifecycle/stage_transition.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/fixtures/registry-lifecycle/version_create.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/fixtures/replay-determinism/fixture-manifest.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/fixtures/replay-determinism/trace.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/fixtures/replay-suite-1/fixture-manifest.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/fixtures/replay-suite-1/trace.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/fixtures/tracking-monitoring/fixture-manifest.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/fixtures/tracking-monitoring/run_event.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/catalog.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/checkpoint-restore/vectors-manifest.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/checkpoint-restore/vectors.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/conformance/canonical_cbor/.gitkeep` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/conformance/canonical_cbor/vectors.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/conformance/interface_hash/.gitkeep` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/conformance/interface_hash/vectors.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Backend_LoadDriver.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Certificate_EvidenceValidate.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Checkpoint_CheckpointMigrate.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Checkpoint_Restore.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Config_ManifestMigrate.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Data_NextBatch.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_DifferentialPrivacy_Apply.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Error_Emit.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_IO_SaveCheckpoint.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Import_LegacyFramework.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Model_Forward.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Model_ModelIR_Executor.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Monitor_DriftCompute.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Monitor_Emit.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Monitor_Register.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Registry_StageTransition.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Registry_VersionCreate.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_TMMU_PrepareMemory.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Trace_TraceMigrate.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Tracking_ArtifactGet.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Tracking_ArtifactList.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Tracking_ArtifactPut.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Tracking_ArtifactTombstone.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Tracking_MetricLog.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Tracking_RunCreate.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Tracking_RunEnd.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Tracking_RunStart.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/conformance/storage/state_recovery_vectors.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/conformance/struct_validation/.gitkeep` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/conformance/struct_validation/vectors.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/failure-injection/vectors-manifest.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/failure-injection/vectors.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/hello-core/vectors-manifest.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/hello-core/vectors.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/perf-scale/vectors-manifest.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/perf-scale/vectors.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/registry-lifecycle/vectors-manifest.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/registry-lifecycle/vectors.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/replay-determinism/vectors-manifest.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/replay-determinism/vectors.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/replay-suite-1/vectors-manifest.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/replay-suite-1/vectors.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/replay-suites/index.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/tracking-monitoring/vectors-manifest.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `artifacts/inputs/vectors/tracking-monitoring/vectors.json` | Deterministic inputs, expected outputs, bundles, or generated artifacts. |
| `distribution/README.md` | Release, packaging, signing, and distribution-facing assets. |
| `distribution/release/CHECKSUMS_v0.1.0.sha256` | Release, packaging, signing, and distribution-facing assets. |
| `distribution/release/CHECKSUMS_v0.1.0.sha256.asc` | Release, packaging, signing, and distribution-facing assets. |
| `distribution/release/RELEASE_NOTES_v0.1.0.md` | Release, packaging, signing, and distribution-facing assets. |
| `distribution/release/RELEASE_PUBKEY.asc` | Release, packaging, signing, and distribution-facing assets. |
| `distribution/release/SIGNING.md` | Release, packaging, signing, and distribution-facing assets. |
| `docs/BRAND.md` | Repository-level configuration or supporting documentation. |
| `docs/HELLO_CORE_NEXT_STEPS.md` | Repository-level configuration or supporting documentation. |
| `docs/START-HERE.md` | Repository-level configuration or supporting documentation. |
| `docs/VERIFY.md` | Repository-level configuration or supporting documentation. |
| `evidence/README.md` | Generated verification evidence, reports, and audit outputs. |
| `evidence/conformance/reports/latest.json` | Generated verification evidence, reports, and audit outputs. |
| `evidence/conformance/results/latest.json` | Generated verification evidence, reports, and audit outputs. |
| `evidence/coverage/operator_coverage.json` | Generated verification evidence, reports, and audit outputs. |
| `evidence/deploy/drift.json` | Generated verification evidence, reports, and audit outputs. |
| `evidence/deploy/latest.json` | Generated verification evidence, reports, and audit outputs. |
| `evidence/deploy/parity.json` | Generated verification evidence, reports, and audit outputs. |
| `evidence/deploy/rollback.json` | Generated verification evidence, reports, and audit outputs. |
| `evidence/deploy/state/staging_active.json` | Generated verification evidence, reports, and audit outputs. |
| `evidence/deploy/state/staging_previous.json` | Generated verification evidence, reports, and audit outputs. |
| `evidence/ga/latest.json` | Generated verification evidence, reports, and audit outputs. |
| `evidence/ga/release_candidate_verification.json` | Generated verification evidence, reports, and audit outputs. |
| `evidence/observability/alert_test.json` | Generated verification evidence, reports, and audit outputs. |
| `evidence/observability/dashboard_inventory.json` | Generated verification evidence, reports, and audit outputs. |
| `evidence/observability/incident_drill.json` | Generated verification evidence, reports, and audit outputs. |
| `evidence/observability/latest.json` | Generated verification evidence, reports, and audit outputs. |
| `evidence/observability/lineage_index.json` | Generated verification evidence, reports, and audit outputs. |
| `evidence/observability/slo_status.json` | Generated verification evidence, reports, and audit outputs. |
| `evidence/observability/synthetic_probe.json` | Generated verification evidence, reports, and audit outputs. |
| `evidence/recovery/backup-restore-drill.json` | Generated verification evidence, reports, and audit outputs. |
| `evidence/recovery/checkpoint-backup.json` | Generated verification evidence, reports, and audit outputs. |
| `evidence/recovery/latest.json` | Generated verification evidence, reports, and audit outputs. |
| `evidence/recovery/replay-proof.txt` | Generated verification evidence, reports, and audit outputs. |
| `evidence/repro/compare-20260228.md` | Generated verification evidence, reports, and audit outputs. |
| `evidence/repro/compare-template.md` | Generated verification evidence, reports, and audit outputs. |
| `evidence/repro/dependency-lock.sha256` | Generated verification evidence, reports, and audit outputs. |
| `evidence/repro/hashes.txt` | Generated verification evidence, reports, and audit outputs. |
| `evidence/repro/run-checklist.md` | Generated verification evidence, reports, and audit outputs. |
| `evidence/runtime_state/checkpoint-restore/ckpt-1.json` | Generated verification evidence, reports, and audit outputs. |
| `evidence/runtime_state/deploy/staging_active.json` | Generated verification evidence, reports, and audit outputs. |
| `evidence/runtime_state/deploy/staging_previous.json` | Generated verification evidence, reports, and audit outputs. |
| `evidence/security/audit.log.jsonl` | Generated verification evidence, reports, and audit outputs. |
| `evidence/security/build_provenance.json` | Generated verification evidence, reports, and audit outputs. |
| `evidence/security/latest.json` | Generated verification evidence, reports, and audit outputs. |
| `evidence/security/sbom.json` | Generated verification evidence, reports, and audit outputs. |
| `evidence/structure/PROJECT_FILE_INVENTORY.md` | Generated verification evidence, reports, and audit outputs. |
| `evidence/structure/domain_dependency_gate.json` | Generated verification evidence, reports, and audit outputs. |
| `evidence/structure/latest.json` | Generated verification evidence, reports, and audit outputs. |
| `evidence/structure/legacy_path_gate.json` | Generated verification evidence, reports, and audit outputs. |
| `evidence/structure/spec_link_gate.json` | Generated verification evidence, reports, and audit outputs. |
| `evidence/structure/spec_schema_map.json` | Generated verification evidence, reports, and audit outputs. |
| `evidence/structure/structural_invariants.json` | Generated verification evidence, reports, and audit outputs. |
| `evidence/validation/external_security_review.md` | Generated verification evidence, reports, and audit outputs. |
| `evidence/validation/independent_verification_summary.json` | Generated verification evidence, reports, and audit outputs. |
| `evidence/validation/issues.json` | Generated verification evidence, reports, and audit outputs. |
| `evidence/validation/latest.json` | Generated verification evidence, reports, and audit outputs. |
| `evidence/validation/runs/run-01-linux-mint.json` | Generated verification evidence, reports, and audit outputs. |
| `evidence/validation/runs/run-02-ubuntu-wsl.json` | Generated verification evidence, reports, and audit outputs. |
| `evidence/validation/runs/run-03-docs-only-cleanroom.json` | Generated verification evidence, reports, and audit outputs. |
| `evidence/validation/scorecards/run-01-linux-mint.json` | Generated verification evidence, reports, and audit outputs. |
| `evidence/validation/scorecards/run-02-ubuntu-wsl.json` | Generated verification evidence, reports, and audit outputs. |
| `evidence/validation/scorecards/run-03-docs-only-cleanroom.json` | Generated verification evidence, reports, and audit outputs. |
| `evidence/validation/transcripts/run-01-linux-mint.md` | Generated verification evidence, reports, and audit outputs. |
| `evidence/validation/transcripts/run-02-ubuntu-wsl.md` | Generated verification evidence, reports, and audit outputs. |
| `evidence/validation/transcripts/run-03-docs-only-cleanroom.md` | Generated verification evidence, reports, and audit outputs. |
| `governance/README.md` | Governance policy, roadmap, lint, ecosystem, or structural control docs. |
| `governance/document_guidelines/EquationCode/BRIDGE.md` | Governance policy, roadmap, lint, ecosystem, or structural control docs. |
| `governance/document_guidelines/EquationCode/ECOSYSTEM.md` | Governance policy, roadmap, lint, ecosystem, or structural control docs. |
| `governance/document_guidelines/EquationCode/EQC.md` | Governance policy, roadmap, lint, ecosystem, or structural control docs. |
| `governance/document_guidelines/EquationCode/LICENSE` | Governance policy, roadmap, lint, ecosystem, or structural control docs. |
| `governance/document_guidelines/EquationCode/README.md` | Governance policy, roadmap, lint, ecosystem, or structural control docs. |
| `governance/ecosystem/ecosystem-compatibility-aggregate.yaml` | Governance policy, roadmap, lint, ecosystem, or structural control docs. |
| `governance/ecosystem/ecosystem-graph.yaml` | Governance policy, roadmap, lint, ecosystem, or structural control docs. |
| `governance/ecosystem/ecosystem-registry.yaml` | Governance policy, roadmap, lint, ecosystem, or structural control docs. |
| `governance/ecosystem/ecosystem-validation-log.md` | Governance policy, roadmap, lint, ecosystem, or structural control docs. |
| `governance/ecosystem/ecosystem.md` | Governance policy, roadmap, lint, ecosystem, or structural control docs. |
| `governance/ecosystem/tooling-manifest.yaml` | Governance policy, roadmap, lint, ecosystem, or structural control docs. |
| `governance/ip/BADGE_PROGRAM_DRAFT.md` | Governance policy, roadmap, lint, ecosystem, or structural control docs. |
| `governance/ip/DEFENSIVE_PUBLICATION_PLAN.md` | Governance policy, roadmap, lint, ecosystem, or structural control docs. |
| `governance/ip/DISCLOSURE-RULES.md` | Governance policy, roadmap, lint, ecosystem, or structural control docs. |
| `governance/ip/IP-POSTURE.md` | Governance policy, roadmap, lint, ecosystem, or structural control docs. |
| `governance/lint/semantic_lint_high_confidence.txt` | Governance policy, roadmap, lint, ecosystem, or structural control docs. |
| `governance/lint/semantic_lint_report.txt` | Governance policy, roadmap, lint, ecosystem, or structural control docs. |
| `governance/process/Community-Governance-Model.md` | Governance policy, roadmap, lint, ecosystem, or structural control docs. |
| `governance/process/Contributing-Workflow.md` | Governance policy, roadmap, lint, ecosystem, or structural control docs. |
| `governance/process/PR-Review-Checklist.md` | Governance policy, roadmap, lint, ecosystem, or structural control docs. |
| `governance/registry/data-registry.yaml` | Governance policy, roadmap, lint, ecosystem, or structural control docs. |
| `governance/roadmap/INTERPRETATION_LOG.md` | Governance policy, roadmap, lint, ecosystem, or structural control docs. |
| `governance/roadmap/WEEKLY_REVIEW_TEMPLATE.md` | Governance policy, roadmap, lint, ecosystem, or structural control docs. |
| `governance/roadmap/migration-plan-template.yaml` | Governance policy, roadmap, lint, ecosystem, or structural control docs. |
| `governance/roadmap/milestones.txt` | Governance policy, roadmap, lint, ecosystem, or structural control docs. |
| `governance/security/OPERATIONS.md` | Governance policy, roadmap, lint, ecosystem, or structural control docs. |
| `governance/security/THREAT_MODEL.md` | Governance policy, roadmap, lint, ecosystem, or structural control docs. |
| `governance/structure/CANONICAL_CBOR_VECTORS_README.md` | Governance policy, roadmap, lint, ecosystem, or structural control docs. |
| `governance/structure/DOCUMENT_AUDIENCE_POLICY.md` | Governance policy, roadmap, lint, ecosystem, or structural control docs. |
| `governance/structure/DOC_CODE_SEPARATION_POLICY.md` | Governance policy, roadmap, lint, ecosystem, or structural control docs. |
| `governance/structure/OPERATOR_STUB_VECTORS_README.txt` | Governance policy, roadmap, lint, ecosystem, or structural control docs. |
| `governance/structure/PHASE1_RESTRUCTURE_MAP.md` | Governance policy, roadmap, lint, ecosystem, or structural control docs. |
| `governance/structure/PHASE2_ARTIFACT_CONSOLIDATION.md` | Governance policy, roadmap, lint, ecosystem, or structural control docs. |
| `governance/structure/PROJECT_FILE_INVENTORY.md` | Governance policy, roadmap, lint, ecosystem, or structural control docs. |
| `governance/structure/STRUCTURAL_INVARIANTS.md` | Governance policy, roadmap, lint, ecosystem, or structural control docs. |
| `governance/structure/spec_link_policy.json` | Governance policy, roadmap, lint, ecosystem, or structural control docs. |
| `governance/structure/spec_schema_map.json` | Governance policy, roadmap, lint, ecosystem, or structural control docs. |
| `governance/structure/templates/PROJECT_FILE_INVENTORY_TEMPLATE.md` | Governance policy, roadmap, lint, ecosystem, or structural control docs. |
| `product/README.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/business/DELIVERABLES_LIST.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/business/FEES.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/business/LOCAL_NETWORK.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/business/OFFERS.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/business/STRUCTURE_TRACK.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/docs/ACCESSIBILITY_REVIEW.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/docs/ANNUAL_SECURITY_REVIEW_POLICY.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/docs/API_CLI_COMMANDS.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/docs/API_LIFECYCLE_POLICY.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/docs/API_REFERENCE_v1.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/docs/API_STYLE_GUIDE.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/docs/CHANGE_COMMUNICATION_SLA.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/docs/COMPLIANCE_EVIDENCE_INDEX.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/docs/DEPENDENCY_LICENSE_REVIEW.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/docs/DOCS_VERSIONING_POLICY.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/docs/GA_COMPATIBILITY_GUARANTEES.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/docs/GA_CONTRACTUAL_SUPPORT_SLA.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/docs/GA_GO_NO_GO_CHECKLIST.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/docs/GA_MIGRATION_GUIDE.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/docs/GA_RELEASE_TRAIN_POLICY.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/docs/GA_SIGNOFF.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/docs/GA_STATUS_INCIDENT_COMMUNICATION.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/docs/GA_SUPPORT_LIFECYCLE.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/docs/GA_SUPPORT_MATRIX.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/docs/GA_SUPPORT_OPERATIONS_READINESS.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/docs/M17_APPROVAL.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/docs/M18_CONTRACT_TEST_REPORT.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/docs/M19_RECOVERY_TEST_REPORT.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/docs/M20_SECURITY_TEST_REPORT.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/docs/M21_DEPLOYMENT_TEST_REPORT.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/docs/M22_OBSERVABILITY_REPORT.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/docs/M23_EXTERNAL_VALIDATION_REPORT.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/docs/M24_GA_RELEASE_REPORT.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/docs/PERSISTENCE_SCHEMA_v1.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/docs/PERSISTENT_STORAGE_ADAPTER_CONTRACT.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/docs/POST_GA_GOVERNANCE.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/docs/PRIVACY_IMPACT_ASSESSMENT_WORKFLOW.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/docs/PRODUCT_SCOPE.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/docs/RUNTIME_PROFILES.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/docs/SUPPLY_CHAIN_TRUST_POLICY.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/docs/how_to/MILESTONE_15_TWO_HOST_RUNBOOK.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/docs/portfolio-release-notes-template.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/docs/reports/CONFORMANCE_REPORT_TEMPLATE.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/docs/reports/INTEGRATION_REPORT_TEMPLATE.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/docs/reports/OUTREACH_2026-02-27.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/docs/reports/merged_docs.txt` | Product-facing documentation, operations guides, and public artifacts. |
| `product/ops/DEPLOYMENT_RUNBOOK.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/ops/INCIDENT_RESPONSE.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/ops/ROLLBACK_RUNBOOK.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/ops/SLOs.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/site/assets/glyphser3.png` | Product-facing documentation, operations guides, and public artifacts. |
| `product/site/assets/glyphser3.svg` | Product-facing documentation, operations guides, and public artifacts. |
| `product/site/services.md` | Product-facing documentation, operations guides, and public artifacts. |
| `product/site/verify.md` | Product-facing documentation, operations guides, and public artifacts. |
| `pyproject.toml` | Repository-level configuration or supporting documentation. |
| `requirements.lock` | Repository-level configuration or supporting documentation. |
| `specs/README.md` | Normative specification, contracts, and layer documentation. |
| `specs/compatibility/CERTIFICATION_DELIVERABLES.md` | Normative specification, contracts, and layer documentation. |
| `specs/compatibility/COMPATIBILITY_CRITERIA_v0.1.md` | Normative specification, contracts, and layer documentation. |
| `specs/compatibility/VENDOR_SELF_TEST_KIT.md` | Normative specification, contracts, and layer documentation. |
| `specs/contracts/capability_catalog.cbor` | Normative specification, contracts, and layer documentation. |
| `specs/contracts/catalog-manifest.json` | Normative specification, contracts, and layer documentation. |
| `specs/contracts/digest_catalog.cbor` | Normative specification, contracts, and layer documentation. |
| `specs/contracts/error_codes.cbor` | Normative specification, contracts, and layer documentation. |
| `specs/contracts/error_codes.json` | Normative specification, contracts, and layer documentation. |
| `specs/contracts/interface_hash.json` | Normative specification, contracts, and layer documentation. |
| `specs/contracts/openapi_public_api_v1.yaml` | Normative specification, contracts, and layer documentation. |
| `specs/contracts/operator_registry.cbor` | Normative specification, contracts, and layer documentation. |
| `specs/contracts/operator_registry.json` | Normative specification, contracts, and layer documentation. |
| `specs/contracts/operator_registry_source.json` | Normative specification, contracts, and layer documentation. |
| `specs/contracts/schema_catalog.cbor` | Normative specification, contracts, and layer documentation. |
| `specs/contracts/vectors_catalog.cbor` | Normative specification, contracts, and layer documentation. |
| `specs/examples/hello-core/hello-core-golden.json` | Normative specification, contracts, and layer documentation. |
| `specs/examples/hello-core/manifest.core.yaml` | Normative specification, contracts, and layer documentation. |
| `specs/examples/operators/Glyphser_IO_SaveCheckpoint.json` | Normative specification, contracts, and layer documentation. |
| `specs/examples/operators/Glyphser_Model_Forward.json` | Normative specification, contracts, and layer documentation. |
| `specs/examples/operators/README.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L1-foundation/API-Interfaces.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L1-foundation/Canonical-CBOR-Profile.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L1-foundation/Data-Structures.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L1-foundation/Dependency-Lock-Policy.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L1-foundation/Determinism-Profiles.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L1-foundation/Digest-Catalog.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L1-foundation/Environment-Manifest.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L1-foundation/Error-Codes.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L1-foundation/Normativity-Legend.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L1-foundation/Operator-Registry-Schema.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L1-foundation/README.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L1-foundation/Redaction-Policy.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L2-specs/AuthZ-Capability-Matrix.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L2-specs/Checkpoint-Schema.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L2-specs/Config-Schema.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L2-specs/Data-Lineage.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L2-specs/Data-NextBatch.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L2-specs/Deployment-Runbook.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L2-specs/DifferentialPrivacy-Apply.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L2-specs/Evaluation-Harness.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L2-specs/Execution-Certificate.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L2-specs/Experiment-Tracking.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L2-specs/Glyphser-Kernel-v3.22-OS.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L2-specs/Model-Registry.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L2-specs/ModelIR-Executor.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L2-specs/Monitoring-Policy.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L2-specs/Pipeline-Orchestrator.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L2-specs/README.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L2-specs/Replay-Determinism.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L2-specs/Run-Commit-WAL.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L2-specs/Security-Compliance-Profile.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L2-specs/TMMU-Allocation.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L2-specs/Trace-Sidecar.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L3-tests/Compatibility-Test-Matrix.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L3-tests/Conformance-CI-Pipeline.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L3-tests/Conformance-Harness-Guide.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L3-tests/Coverage-Targets.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L3-tests/Data-Contract-Fuzzing-Guide.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L3-tests/Failure-Injection-Index.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L3-tests/Failure-Injection-Scenarios.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L3-tests/Game-Day-Scenarios.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L3-tests/Integration-Test-Matrix.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L3-tests/Operator-Vectors.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L3-tests/Performance-Plan.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L3-tests/README.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L3-tests/Release-Gates.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L3-tests/Storage-Recovery-Test-Matrix.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L3-tests/Test-Coverage-Gaps.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L3-tests/Test-Inventory.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L3-tests/Test-Plan.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L3-tests/Test-Vectors-Catalog.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/API-Lifecycle-and-Deprecation-Policy.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Algorithm-Closure.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Architecture-Decisions-Log.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Artifact-Store-Adapter-Guide.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Backend-Adapter-Guide.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Backend-Feature-Matrix.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Benchmark-Evidence-Spec.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Brownfield-Deployment-Guide.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Build-and-CI-Matrix.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/CLI-Command-Profiles.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Canonical-Hashing-Reference.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Change-Control-Playbook.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Code-Generation-Mapping.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Coding-Standards.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Command-Reference.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Common-Pitfalls-Guide.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Contracts-Artifact-Lifecycle.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Debugging-Playbook.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Deployment-Generation-Profile.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Determinism-Audit-Playbook.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Determinism-Debug-Checklist.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Deterministic-RNG-Implementation-Guide.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Developer-Setup.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Developer-Troubleshooting-FAQ.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Disaster-Recovery-Operations-Runbook.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Distributed-Failure-Recovery-Guide.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/EQC-CI-Policy.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Ecosystem-Expansion-Roadmap.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Evidence-Catalog.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Expansion-Catalog-041-250.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/External-Interface-Standard.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Fixtures-and-Golden-Data.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Formal-Verification-Roadmap.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Gentle-Introduction.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Hello-World-End-to-End-Example.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Implementation-Backlog.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Implementation-Roadmap.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Incident-Postmortem-Template.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Industry-Productization-Upgrade-Plan.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Interoperability-Standards-Bridge.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Local-Replay-Runbook.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Migration-Execution-Guide.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Module-Scaffolding-Guide.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Operator-Conformance-Matrix.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Operator-Readiness-Checklist.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Operator-Registry-CBOR-Contract.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Operator-SDK-Scaffold-Template.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Profiling-and-Optimization-Guide.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/README.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Reference-Implementations.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Reference-Stack-Minimal.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Release-Evidence-Assembler.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Repo-Layout-and-Interfaces.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Research-Extensions-Roadmap.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Runtime-State-Machine-Reference.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/SDK-Usage-Guide.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/SRE-Incident-Triage-Playbook.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Schema-Evolution-Playbook.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Scope-and-Non-Goals.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Security-Case-Template.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Security-Coding-Checklist.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Spec-Lint-Implementation.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Spec-Lint-Rules.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Target-Architecture-Profile.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Test-Harness-Implementation.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Third-Party-Operator-Certification-Program.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Threat-Model-and-Control-Crosswalk.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Tooling-Suite.md` | Normative specification, contracts, and layer documentation. |
| `specs/layers/L4-implementation/Tooling-and-Automation-Suite.md` | Normative specification, contracts, and layer documentation. |
| `specs/policies/COMPATIBILITY_POLICY.md` | Normative specification, contracts, and layer documentation. |
| `specs/policies/CONFORMANCE_SUITE_v0.1.md` | Normative specification, contracts, and layer documentation. |
| `specs/policies/DETERMINISM_PROFILE_v0.1.md` | Normative specification, contracts, and layer documentation. |
| `specs/policies/ERROR_CODES.md` | Normative specification, contracts, and layer documentation. |
| `specs/policies/NUMERIC_POLICY_v0.1.md` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/README.md` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/SCHEMA_CONVENTIONS.txt` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/SCHEMA_FORMAT_DECISION.txt` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/contract_schema_meta.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L1/README.md` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L1/l1_api_interfaces.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L1/l1_canonical_cbor_profile.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L1/l1_data_structures.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L1/l1_dependency_lock_policy.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L1/l1_determinism_profiles.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L1/l1_digest_catalog.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L1/l1_environment_manifest.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L1/l1_error_codes.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L1/l1_normativity_legend.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L1/l1_operator_registry_schema.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L1/l1_redaction_policy.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L2/README.md` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L2/l2_authz-capability-matrix.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L2/l2_checkpoint-schema.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L2/l2_config-schema.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L2/l2_data-lineage.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L2/l2_data-nextbatch.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L2/l2_deployment-runbook.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L2/l2_differentialprivacy-apply.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L2/l2_evaluation-harness.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L2/l2_execution-certificate.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L2/l2_experiment-tracking.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L2/l2_glyphser-kernel-v3.22-os.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L2/l2_model-registry.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L2/l2_modelir-executor.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L2/l2_monitoring-policy.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L2/l2_pipeline-orchestrator.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L2/l2_replay-determinism.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L2/l2_run-commit-wal.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L2/l2_security-compliance-profile.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L2/l2_tmmu-allocation.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L2/l2_trace-sidecar.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L3/README.md` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L3/l3_compatibility-test-matrix.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L3/l3_conformance-ci-pipeline.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L3/l3_conformance-harness-guide.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L3/l3_coverage-targets.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L3/l3_data-contract-fuzzing-guide.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L3/l3_failure-injection-index.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L3/l3_failure-injection-scenarios.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L3/l3_game-day-scenarios.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L3/l3_integration-test-matrix.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L3/l3_operator_error_vectors.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L3/l3_operator_vectors.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L3/l3_performance-plan.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L3/l3_release-gates.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L3/l3_storage-recovery-test-matrix.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L3/l3_test-plan.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L3/l3_test-vectors-catalog.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/README.md` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_api-lifecycle-and-deprecation-policy.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_architecture-decisions-log.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_artifact-store-adapter-guide.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_backend-adapter-guide.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_backend-feature-matrix.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_benchmark-evidence-spec.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_brownfield-deployment-guide.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_build-and-ci-matrix.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_canonical-hashing-reference.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_change-control-playbook.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_cli-command-profiles.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_code-generation-mapping.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_coding-standards.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_command-reference.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_common-pitfalls-guide.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_community-governance-model.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_contracts-artifact-lifecycle.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_contributing-workflow.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_debugging-playbook.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_determinism-audit-playbook.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_determinism-debug-checklist.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_deterministic-rng-implementation-guide.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_developer-setup.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_developer-troubleshooting-faq.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_disaster-recovery-operations-runbook.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_distributed-failure-recovery-guide.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_ecosystem-expansion-roadmap.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_eqc-ci-policy.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_evidence-catalog.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_expansion-catalog-041-250.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_external-interface-standard.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_fixtures-and-golden-data.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_formal-verification-roadmap.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_gentle-introduction.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_hello-world-end-to-end-example.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_implementation-backlog.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_implementation-roadmap.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_incident-postmortem-template.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_industry-productization-upgrade-plan.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_interoperability-standards-bridge.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_local-replay-runbook.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_migration-execution-guide.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_module-scaffolding-guide.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_operator-conformance-matrix.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_operator-registry-cbor-contract.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_operator-sdk-scaffold-template.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_pr-review-checklist.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_profiling-and-optimization-guide.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_reference-implementations.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_reference-stack-minimal.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_release-evidence-assembler.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_repo-layout-and-interfaces.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_research-extensions-roadmap.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_runtime-state-machine-reference.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_schema-evolution-playbook.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_scope-and-non-goals.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_sdk-usage-guide.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_security-case-template.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_security-coding-checklist.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_spec-lint-implementation.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_spec-lint-rules.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_sre-incident-triage-playbook.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_test-harness-implementation.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_third-party-operator-certification-program.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_threat-model-and-control-crosswalk.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_tooling-and-automation-suite.schema.json` | Normative specification, contracts, and layer documentation. |
| `specs/schemas/layers/L4/l4_tooling-suite.schema.json` | Normative specification, contracts, and layer documentation. |
| `src/glyphser/api/runtime_api.py` | Runtime source code and importable application modules. |
| `src/glyphser/api/validate_signature.py` | Runtime source code and importable application modules. |
| `src/glyphser/backend/load_driver.py` | Runtime source code and importable application modules. |
| `src/glyphser/backend/reference_driver.py` | Runtime source code and importable application modules. |
| `src/glyphser/cert/evidence_validate.py` | Runtime source code and importable application modules. |
| `src/glyphser/certificate/build.py` | Runtime source code and importable application modules. |
| `src/glyphser/checkpoint/migrate_checkpoint.py` | Runtime source code and importable application modules. |
| `src/glyphser/checkpoint/restore.py` | Runtime source code and importable application modules. |
| `src/glyphser/checkpoint/write.py` | Runtime source code and importable application modules. |
| `src/glyphser/config/migrate_manifest.py` | Runtime source code and importable application modules. |
| `src/glyphser/contract/validate.py` | Runtime source code and importable application modules. |
| `src/glyphser/data/next_batch.py` | Runtime source code and importable application modules. |
| `src/glyphser/data_structures/validate_struct.py` | Runtime source code and importable application modules. |
| `src/glyphser/dp/apply.py` | Runtime source code and importable application modules. |
| `src/glyphser/error/emit.py` | Runtime source code and importable application modules. |
| `src/glyphser/fingerprint/state_fingerprint.py` | Runtime source code and importable application modules. |
| `src/glyphser/legacy_import/legacy_framework.py` | Runtime source code and importable application modules. |
| `src/glyphser/model/build_grad_dependency_order.py` | Runtime source code and importable application modules. |
| `src/glyphser/model/collect_gradients.py` | Runtime source code and importable application modules. |
| `src/glyphser/model/dispatch_primitive.py` | Runtime source code and importable application modules. |
| `src/glyphser/model/forward.py` | Runtime source code and importable application modules. |
| `src/glyphser/model/ir_schema.py` | Runtime source code and importable application modules. |
| `src/glyphser/model/model_ir_executor.py` | Runtime source code and importable application modules. |
| `src/glyphser/model/topo_sort_nodes.py` | Runtime source code and importable application modules. |
| `src/glyphser/monitor/drift_compute.py` | Runtime source code and importable application modules. |
| `src/glyphser/monitor/emit.py` | Runtime source code and importable application modules. |
| `src/glyphser/monitor/register.py` | Runtime source code and importable application modules. |
| `src/glyphser/registry/interface_hash.py` | Runtime source code and importable application modules. |
| `src/glyphser/registry/registry_builder.py` | Runtime source code and importable application modules. |
| `src/glyphser/registry/stage_transition.py` | Runtime source code and importable application modules. |
| `src/glyphser/registry/version_create.py` | Runtime source code and importable application modules. |
| `src/glyphser/security/__init__.py` | Runtime source code and importable application modules. |
| `src/glyphser/security/audit.py` | Runtime source code and importable application modules. |
| `src/glyphser/security/authz.py` | Runtime source code and importable application modules. |
| `src/glyphser/serialization/canonical_cbor.py` | Runtime source code and importable application modules. |
| `src/glyphser/storage/__init__.py` | Runtime source code and importable application modules. |
| `src/glyphser/storage/state_store.py` | Runtime source code and importable application modules. |
| `src/glyphser/tmmu/commit_execution.py` | Runtime source code and importable application modules. |
| `src/glyphser/tmmu/prepare_memory.py` | Runtime source code and importable application modules. |
| `src/glyphser/trace/compute_trace_hash.py` | Runtime source code and importable application modules. |
| `src/glyphser/trace/migrate_trace.py` | Runtime source code and importable application modules. |
| `src/glyphser/trace/trace_sidecar.py` | Runtime source code and importable application modules. |
| `src/glyphser/tracking/artifact_get.py` | Runtime source code and importable application modules. |
| `src/glyphser/tracking/artifact_list.py` | Runtime source code and importable application modules. |
| `src/glyphser/tracking/artifact_put.py` | Runtime source code and importable application modules. |
| `src/glyphser/tracking/artifact_tombstone.py` | Runtime source code and importable application modules. |
| `src/glyphser/tracking/metric_log.py` | Runtime source code and importable application modules. |
| `src/glyphser/tracking/run_create.py` | Runtime source code and importable application modules. |
| `src/glyphser/tracking/run_end.py` | Runtime source code and importable application modules. |
| `src/glyphser/tracking/run_start.py` | Runtime source code and importable application modules. |
| `tests/__init__.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/api/__init__.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/api/test_api_cli.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/api/test_api_contract_gate.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/api/test_runtime_api.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/api/test_validate_signature.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/canonical_cbor/__init__.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/canonical_cbor/test_fuzz.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/canonical_cbor/test_vectors.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/canonical_cbor/vector_loader.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/chaos/test_distributed_chaos.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/conftest.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/data_structures/__init__.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/data_structures/test_validate_struct.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/data_structures/test_vectors.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/deploy/test_deploy_pipeline_gate.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/fixtures/test_mini_tracking_fixture.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/fuzz/test_checkpoint_decode_fuzz.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/fuzz/test_ir_validation_fuzz.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/fuzz/test_manifest_parser_fuzz.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/fuzz/test_schema_parsing_fuzz.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/fuzz/test_tmmu_planner_invariants.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/fuzz/test_trace_parser_fuzz.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/ga/test_ga_release_gate.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/goldens/test_golden_inventory.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/interface_hash/__init__.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/interface_hash/test_vectors.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/operators/__init__.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/operators/test_glyphser_backend_stubs.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/operators/test_glyphser_certificate_stubs.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/operators/test_glyphser_checkpoint_stubs.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/operators/test_glyphser_config_stubs.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/operators/test_glyphser_data_stubs.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/operators/test_glyphser_differentialprivacy_stubs.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/operators/test_glyphser_error_stubs.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/operators/test_glyphser_import_stubs.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/operators/test_glyphser_io_stubs.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/operators/test_glyphser_model_stubs.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/operators/test_glyphser_monitor_stubs.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/operators/test_glyphser_registry_stubs.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/operators/test_glyphser_tmmu_stubs.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/operators/test_glyphser_trace_stubs.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/operators/test_glyphser_tracking_stubs.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/ops/test_doc_code_separation_gate.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/ops/test_domain_dependency_gate.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/ops/test_legacy_path_gate.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/ops/test_observability_gate.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/ops/test_spec_link_gate.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/ops/test_spec_schema_map_gate.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/ops/test_structural_invariants_gate.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/replay/test_determinism_regression_matrix.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/replay/test_replay_divergence.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/security/test_authz_and_audit.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/security/test_security_baseline_gate.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/storage/test_state_store_recovery.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/test_determinism_repeat.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/test_error_codes_manifest.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/test_error_emit.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/test_operator_vectors.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/test_replay_binding.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/test_replay_suite.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/test_smoke.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/trace/__init__.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/trace/test_compute_trace_hash.py` | Automated test coverage across unit/integration/conformance domains. |
| `tests/validation/test_external_validation_gate.py` | Automated test coverage across unit/integration/conformance domains. |
| `tooling/README.md` | Automation, gate, build, release, or developer tooling script. |
| `tooling/__init__.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/cli/__init__.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/cli/api_cli.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/cli/conformance_cli.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/codegen/__init__.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/codegen/check_generated_drift.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/codegen/cleanroom_validation.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/codegen/cleanroom_validation_generate.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/codegen/diff_fidelity.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/codegen/generate.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/codegen/input_hash_manifest.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/codegen/run_and_test.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/codegen/templates/bindings.py.tpl` | Automation, gate, build, release, or developer tooling script. |
| `tooling/codegen/templates/error.py.tpl` | Automation, gate, build, release, or developer tooling script. |
| `tooling/codegen/templates/models.py.tpl` | Automation, gate, build, release, or developer tooling script. |
| `tooling/codegen/templates/operators.py.tpl` | Automation, gate, build, release, or developer tooling script. |
| `tooling/codegen/templates/validators.py.tpl` | Automation, gate, build, release, or developer tooling script. |
| `tooling/conformance/__init__.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/conformance/cli.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/conformance/report_template.json` | Automation, gate, build, release, or developer tooling script. |
| `tooling/deploy/__init__.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/deploy/deploy_rollback_gate.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/deploy/generate_bundle.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/deploy/generate_env_manifest.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/deploy/generate_migration_plan.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/deploy/generate_overlays.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/deploy/overlay_templates/dev.json` | Automation, gate, build, release, or developer tooling script. |
| `tooling/deploy/overlay_templates/prod.json` | Automation, gate, build, release, or developer tooling script. |
| `tooling/deploy/overlay_templates/staging.json` | Automation, gate, build, release, or developer tooling script. |
| `tooling/deploy/run_deployment_pipeline.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/deploy/templates/policy_bindings.json.tpl` | Automation, gate, build, release, or developer tooling script. |
| `tooling/deploy/templates/runtime_config.json.tpl` | Automation, gate, build, release, or developer tooling script. |
| `tooling/deploy/validate_profile.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/docs/__init__.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/docs/materialize_doc_artifacts.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/docs/merge_markdown_to_txt.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/docs/verify_doc_artifacts.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/gates/__init__.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/gates/api_contract_gate.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/gates/coverage_report.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/gates/doc_code_separation_gate.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/gates/domain_dependency_gate.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/gates/error_code_gate.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/gates/external_validation_gate.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/gates/fixtures_gate.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/gates/legacy_path_gate.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/gates/observability_gate.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/gates/registry_gate.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/gates/schema_gate.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/gates/spec_link_gate.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/gates/spec_lint.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/gates/spec_schema_map_gate.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/gates/state_recovery_gate.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/gates/structural_invariants_gate.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/gates/vector_gate.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/path_config.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/push_button.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/registry/__init__.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/registry/build_operator_registry.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/registry/operator_vectors.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/release/__init__.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/release/build_release_bundle.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/release/ga_release_gate.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/release/release_evidence_gate.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/release/reproducibility_check.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/release/verify_release.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/scripts/repro/host_meta.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/scripts/run_hello_core.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/security/__init__.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/security/security_artifacts.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/security/security_baseline_gate.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/validation/__init__.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/validation/generate_project_inventory.py` | Automation, gate, build, release, or developer tooling script. |
| `tooling/validation/validate_data_integrity.py` | Automation, gate, build, release, or developer tooling script. |
