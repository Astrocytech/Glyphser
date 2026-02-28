# Project File Inventory

Generated: 2026-02-28 14:07:00 UTC

Scope: Full repository tree excluding transient local cache directories (`.git`, `.venv`, `.pytest_cache`, `__pycache__`).

## Full Tree Structure
```text
.
├── .github
│   └── workflows
│       ├── conformance-gate.yml
│       ├── push-button.yml
│       ├── registry-gate.yml
│       └── schema-gate.yml
├── assets
│   ├── glyphser3.png
│   └── glyphser3.svg
├── conformance
│   ├── reports
│   │   └── latest.json
│   ├── results
│   │   └── latest.json
│   ├── vectors
│   │   ├── canonical_cbor
│   │   │   ├── .gitkeep
│   │   │   └── vectors.json
│   │   ├── interface_hash
│   │   │   ├── .gitkeep
│   │   │   └── vectors.json
│   │   └── struct_validation
│   │       ├── .gitkeep
│   │       └── vectors.json
│   └── .gitkeep
├── contracts
│   ├── capability_catalog.cbor
│   ├── catalog-manifest.json
│   ├── digest_catalog.cbor
│   ├── error_codes.cbor
│   ├── error_codes.json
│   ├── interface_hash.json
│   ├── openapi_public_api_v1.yaml
│   ├── operator_registry.cbor
│   ├── operator_registry.json
│   ├── operator_registry_source.json
│   ├── schema_catalog.cbor
│   └── vectors_catalog.cbor
├── dist
│   ├── hello-core-bundle.sha256
│   └── hello-core-bundle.tar.gz
├── docs
│   ├── business
│   │   ├── DELIVERABLES_LIST.md
│   │   ├── FEES.md
│   │   ├── LOCAL_NETWORK.md
│   │   ├── OFFERS.md
│   │   └── STRUCTURE_TRACK.md
│   ├── compatibility
│   │   ├── CERTIFICATION_DELIVERABLES.md
│   │   ├── COMPATIBILITY_CRITERIA_v0.1.md
│   │   └── VENDOR_SELF_TEST_KIT.md
│   ├── contracts
│   │   ├── COMPATIBILITY_POLICY.md
│   │   ├── CONFORMANCE_SUITE_v0.1.md
│   │   ├── DETERMINISM_PROFILE_v0.1.md
│   │   ├── ERROR_CODES.md
│   │   └── NUMERIC_POLICY_v0.1.md
│   ├── examples
│   │   ├── hello-core
│   │   │   ├── hello-core-golden.json
│   │   │   └── manifest.core.yaml
│   │   └── operators
│   │       ├── Glyphser_Backend_LoadDriver.json
│   │       ├── Glyphser_Certificate_EvidenceValidate.json
│   │       ├── Glyphser_Checkpoint_CheckpointMigrate.json
│   │       ├── Glyphser_Checkpoint_Restore.json
│   │       ├── Glyphser_Config_ManifestMigrate.json
│   │       ├── Glyphser_Data_NextBatch.json
│   │       ├── Glyphser_DifferentialPrivacy_Apply.json
│   │       ├── Glyphser_Error_Emit.json
│   │       ├── Glyphser_Import_LegacyFramework.json
│   │       ├── Glyphser_IO_SaveCheckpoint.json
│   │       ├── Glyphser_Model_Forward.json
│   │       ├── Glyphser_Model_ModelIR_Executor.json
│   │       ├── Glyphser_Monitor_DriftCompute.json
│   │       ├── Glyphser_Monitor_Emit.json
│   │       ├── Glyphser_Monitor_Register.json
│   │       ├── Glyphser_Registry_StageTransition.json
│   │       ├── Glyphser_Registry_VersionCreate.json
│   │       ├── Glyphser_TMMU_PrepareMemory.json
│   │       ├── Glyphser_Trace_TraceMigrate.json
│   │       ├── Glyphser_Tracking_ArtifactGet.json
│   │       ├── Glyphser_Tracking_ArtifactList.json
│   │       ├── Glyphser_Tracking_ArtifactPut.json
│   │       ├── Glyphser_Tracking_ArtifactTombstone.json
│   │       ├── Glyphser_Tracking_MetricLog.json
│   │       ├── Glyphser_Tracking_RunCreate.json
│   │       ├── Glyphser_Tracking_RunEnd.json
│   │       └── Glyphser_Tracking_RunStart.json
│   ├── how_to
│   │   └── MILESTONE_15_TWO_HOST_RUNBOOK.md
│   ├── ip
│   │   ├── BADGE_PROGRAM_DRAFT.md
│   │   ├── DEFENSIVE_PUBLICATION_PLAN.md
│   │   ├── DISCLOSURE-RULES.md
│   │   └── IP-POSTURE.md
│   ├── layer1-foundation
│   │   ├── API-Interfaces.md
│   │   ├── Canonical-CBOR-Profile.md
│   │   ├── Data-Structures.md
│   │   ├── Dependency-Lock-Policy.md
│   │   ├── Determinism-Profiles.md
│   │   ├── Digest-Catalog.md
│   │   ├── Environment-Manifest.md
│   │   ├── Error-Codes.md
│   │   ├── Normativity-Legend.md
│   │   ├── Operator-Registry-Schema.md
│   │   └── Redaction-Policy.md
│   ├── layer2-specs
│   │   ├── AuthZ-Capability-Matrix.md
│   │   ├── Checkpoint-Schema.md
│   │   ├── Config-Schema.md
│   │   ├── Data-Lineage.md
│   │   ├── Data-NextBatch.md
│   │   ├── Deployment-Runbook.md
│   │   ├── DifferentialPrivacy-Apply.md
│   │   ├── Evaluation-Harness.md
│   │   ├── Execution-Certificate.md
│   │   ├── Experiment-Tracking.md
│   │   ├── Glyphser-Kernel-v3.22-OS.md
│   │   ├── Model-Registry.md
│   │   ├── ModelIR-Executor.md
│   │   ├── Monitoring-Policy.md
│   │   ├── Pipeline-Orchestrator.md
│   │   ├── Replay-Determinism.md
│   │   ├── Run-Commit-WAL.md
│   │   ├── Security-Compliance-Profile.md
│   │   ├── TMMU-Allocation.md
│   │   └── Trace-Sidecar.md
│   ├── layer3-tests
│   │   ├── Compatibility-Test-Matrix.md
│   │   ├── Conformance-CI-Pipeline.md
│   │   ├── Conformance-Harness-Guide.md
│   │   ├── Coverage-Targets.md
│   │   ├── Data-Contract-Fuzzing-Guide.md
│   │   ├── Failure-Injection-Index.md
│   │   ├── Failure-Injection-Scenarios.md
│   │   ├── Game-Day-Scenarios.md
│   │   ├── Integration-Test-Matrix.md
│   │   ├── Operator-Vectors.md
│   │   ├── Performance-Plan.md
│   │   ├── Release-Gates.md
│   │   ├── Storage-Recovery-Test-Matrix.md
│   │   ├── Test-Coverage-Gaps.md
│   │   ├── Test-Inventory.md
│   │   ├── Test-Plan.md
│   │   └── Test-Vectors-Catalog.md
│   ├── layer4-implementation
│   │   ├── Algorithm-Closure.md
│   │   ├── API-Lifecycle-and-Deprecation-Policy.md
│   │   ├── Architecture-Decisions-Log.md
│   │   ├── Artifact-Store-Adapter-Guide.md
│   │   ├── Backend-Adapter-Guide.md
│   │   ├── Backend-Feature-Matrix.md
│   │   ├── Benchmark-Evidence-Spec.md
│   │   ├── Brownfield-Deployment-Guide.md
│   │   ├── Build-and-CI-Matrix.md
│   │   ├── Canonical-Hashing-Reference.md
│   │   ├── Change-Control-Playbook.md
│   │   ├── CLI-Command-Profiles.md
│   │   ├── Code-Generation-Mapping.md
│   │   ├── Coding-Standards.md
│   │   ├── Command-Reference.md
│   │   ├── Common-Pitfalls-Guide.md
│   │   ├── Community-Governance-Model.md
│   │   ├── Contracts-Artifact-Lifecycle.md
│   │   ├── Contributing-Workflow.md
│   │   ├── Debugging-Playbook.md
│   │   ├── Deployment-Generation-Profile.md
│   │   ├── Determinism-Audit-Playbook.md
│   │   ├── Determinism-Debug-Checklist.md
│   │   ├── Deterministic-RNG-Implementation-Guide.md
│   │   ├── Developer-Setup.md
│   │   ├── Developer-Troubleshooting-FAQ.md
│   │   ├── Disaster-Recovery-Operations-Runbook.md
│   │   ├── Distributed-Failure-Recovery-Guide.md
│   │   ├── Ecosystem-Expansion-Roadmap.md
│   │   ├── EQC-CI-Policy.md
│   │   ├── Evidence-Catalog.md
│   │   ├── Expansion-Catalog-041-250.md
│   │   ├── External-Interface-Standard.md
│   │   ├── Fixtures-and-Golden-Data.md
│   │   ├── Formal-Verification-Roadmap.md
│   │   ├── Gentle-Introduction.md
│   │   ├── Hello-World-End-to-End-Example.md
│   │   ├── Implementation-Backlog.md
│   │   ├── Implementation-Roadmap.md
│   │   ├── Incident-Postmortem-Template.md
│   │   ├── Industry-Productization-Upgrade-Plan.md
│   │   ├── Interoperability-Standards-Bridge.md
│   │   ├── Local-Replay-Runbook.md
│   │   ├── Migration-Execution-Guide.md
│   │   ├── Module-Scaffolding-Guide.md
│   │   ├── Operator-Conformance-Matrix.md
│   │   ├── Operator-Readiness-Checklist.md
│   │   ├── Operator-Registry-CBOR-Contract.md
│   │   ├── Operator-SDK-Scaffold-Template.md
│   │   ├── PR-Review-Checklist.md
│   │   ├── Profiling-and-Optimization-Guide.md
│   │   ├── Reference-Implementations.md
│   │   ├── Reference-Stack-Minimal.md
│   │   ├── Release-Evidence-Assembler.md
│   │   ├── Repo-Layout-and-Interfaces.md
│   │   ├── Research-Extensions-Roadmap.md
│   │   ├── Runtime-State-Machine-Reference.md
│   │   ├── Schema-Evolution-Playbook.md
│   │   ├── Scope-and-Non-Goals.md
│   │   ├── SDK-Usage-Guide.md
│   │   ├── Security-Case-Template.md
│   │   ├── Security-Coding-Checklist.md
│   │   ├── Spec-Lint-Implementation.md
│   │   ├── Spec-Lint-Rules.md
│   │   ├── SRE-Incident-Triage-Playbook.md
│   │   ├── Target-Architecture-Profile.md
│   │   ├── Test-Harness-Implementation.md
│   │   ├── Third-Party-Operator-Certification-Program.md
│   │   ├── Threat-Model-and-Control-Crosswalk.md
│   │   ├── Tooling-and-Automation-Suite.md
│   │   └── Tooling-Suite.md
│   ├── ops
│   │   ├── DEPLOYMENT_RUNBOOK.md
│   │   ├── INCIDENT_RESPONSE.md
│   │   ├── ROLLBACK_RUNBOOK.md
│   │   └── SLOs.md
│   ├── product
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
│   │   ├── POST_GA_GOVERNANCE.md
│   │   ├── PRIVACY_IMPACT_ASSESSMENT_WORKFLOW.md
│   │   ├── PRODUCT_SCOPE.md
│   │   ├── RUNTIME_PROFILES.md
│   │   └── SUPPLY_CHAIN_TRUST_POLICY.md
│   ├── release
│   │   ├── CHECKSUMS_v0.1.0.sha256
│   │   ├── CHECKSUMS_v0.1.0.sha256.asc
│   │   ├── RELEASE_PUBKEY.asc
│   │   └── SIGNING.md
│   ├── reports
│   │   ├── CONFORMANCE_REPORT_TEMPLATE.md
│   │   ├── INTEGRATION_REPORT_TEMPLATE.md
│   │   ├── merged_docs.txt
│   │   └── OUTREACH_2026-02-27.md
│   ├── security
│   │   ├── OPERATIONS.md
│   │   └── THREAT_MODEL.md
│   ├── site
│   │   ├── services.md
│   │   └── verify.md
│   ├── structure
│   │   ├── CANONICAL_CBOR_VECTORS_README.md
│   │   ├── DOC_CODE_SEPARATION_POLICY.md
│   │   └── OPERATOR_STUB_VECTORS_README.txt
│   ├── BRAND.md
│   ├── HELLO_CORE_NEXT_STEPS.md
│   ├── INTERPRETATION_LOG.md
│   ├── START-HERE.md
│   ├── VERIFY.md
│   └── WEEKLY_REVIEW_TEMPLATE.md
├── document_guidelines
│   └── EquationCode
│       ├── BRIDGE.md
│       ├── ECOSYSTEM.md
│       ├── EQC.md
│       ├── LICENSE
│       └── README.md
├── ecosystem
│   └── tooling-manifest.yaml
├── fixtures
│   ├── checkpoint-restore
│   │   ├── checkpoint_input.json
│   │   ├── fixture-manifest.json
│   │   └── restore_request.json
│   ├── failure-injection
│   │   ├── faulty_request.json
│   │   └── fixture-manifest.json
│   ├── hello-core
│   │   ├── checkpoint.json
│   │   ├── execution_certificate.json
│   │   ├── fixture-manifest.json
│   │   ├── manifest.core.yaml
│   │   ├── model_ir.json
│   │   ├── tiny_synth_dataset.jsonl
│   │   └── trace.json
│   ├── mini-tracking
│   │   └── inputs.json
│   ├── perf-scale
│   │   ├── batch.json
│   │   └── fixture-manifest.json
│   ├── registry-lifecycle
│   │   ├── fixture-manifest.json
│   │   ├── stage_transition.json
│   │   └── version_create.json
│   ├── replay-determinism
│   │   ├── fixture-manifest.json
│   │   └── trace.json
│   ├── replay-suite-1
│   │   ├── fixture-manifest.json
│   │   └── trace.json
│   └── tracking-monitoring
│       ├── fixture-manifest.json
│       └── run_event.json
├── generated
│   ├── clean_build
│   │   ├── bindings.py
│   │   ├── error.py
│   │   ├── models.py
│   │   ├── operators.py
│   │   └── validators.py
│   ├── deploy
│   │   ├── confidential
│   │   │   ├── bundle_manifest.json
│   │   │   ├── policy_bindings.json
│   │   │   └── runtime_config.json
│   │   ├── managed
│   │   │   ├── bundle_manifest.json
│   │   │   ├── policy_bindings.json
│   │   │   └── runtime_config.json
│   │   ├── overlays
│   │   │   ├── dev.json
│   │   │   ├── index.json
│   │   │   ├── prod.json
│   │   │   └── staging.json
│   │   ├── regulated
│   │   │   ├── bundle_manifest.json
│   │   │   ├── policy_bindings.json
│   │   │   └── runtime_config.json
│   │   ├── env_manifest.json
│   │   └── migration_plan.json
│   ├── bindings.py
│   ├── codegen_manifest.json
│   ├── error.py
│   ├── input_hashes.json
│   ├── models.py
│   ├── operators.py
│   └── validators.py
├── goldens
│   ├── checkpoint-restore
│   │   ├── checkpoint_expected.json
│   │   ├── golden-manifest.json
│   │   └── restore_expected.json
│   ├── failure-injection
│   │   ├── faulty_expected.json
│   │   └── golden-manifest.json
│   ├── hello-core
│   │   ├── checkpoint_header.json
│   │   ├── execution_certificate.json
│   │   ├── golden-identities.json
│   │   ├── golden-manifest.json
│   │   └── trace_snippet.json
│   ├── mini-tracking
│   │   └── expected.json
│   ├── perf-scale
│   │   ├── forward_expected.json
│   │   └── golden-manifest.json
│   ├── registry-lifecycle
│   │   ├── golden-manifest.json
│   │   ├── stage_transition_expected.json
│   │   └── version_create_expected.json
│   ├── replay-determinism
│   │   ├── golden-manifest.json
│   │   └── replay_expected.json
│   ├── replay-suite-1
│   │   ├── golden-manifest.json
│   │   └── trace_expected.json
│   ├── tracking-monitoring
│   │   ├── golden-manifest.json
│   │   └── metric_log_expected.json
│   └── golden_inventory.json
├── reports
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
│   ├── security
│   │   ├── audit.log.jsonl
│   │   ├── build_provenance.json
│   │   ├── latest.json
│   │   └── sbom.json
│   ├── structure
│   │   └── latest.json
│   └── validation
│       ├── runs
│       │   ├── run-01-linux-mint.json
│       │   ├── run-02-ubuntu-wsl.json
│       │   └── run-03-docs-only-cleanroom.json
│       ├── scorecards
│       │   ├── run-01-linux-mint.json
│       │   ├── run-02-ubuntu-wsl.json
│       │   └── run-03-docs-only-cleanroom.json
│       ├── transcripts
│       │   ├── run-01-linux-mint.md
│       │   ├── run-02-ubuntu-wsl.md
│       │   └── run-03-docs-only-cleanroom.md
│       ├── external_security_review.md
│       ├── independent_verification_summary.json
│       ├── issues.json
│       └── latest.json
├── schemas
│   ├── pilot
│   │   ├── l1_api_interfaces.schema.json
│   │   ├── l1_canonical_cbor_profile.schema.json
│   │   ├── l1_data_structures.schema.json
│   │   ├── l1_dependency_lock_policy.schema.json
│   │   ├── l1_determinism_profiles.schema.json
│   │   ├── l1_digest_catalog.schema.json
│   │   ├── l1_environment_manifest.schema.json
│   │   ├── l1_error_codes.schema.json
│   │   ├── l1_normativity_legend.schema.json
│   │   ├── l1_operator_registry_schema.schema.json
│   │   ├── l1_redaction_policy.schema.json
│   │   ├── l2_authz-capability-matrix.schema.json
│   │   ├── l2_checkpoint-schema.schema.json
│   │   ├── l2_config-schema.schema.json
│   │   ├── l2_config_schema.schema.json
│   │   ├── l2_data-lineage.schema.json
│   │   ├── l2_data-nextbatch.schema.json
│   │   ├── l2_deployment-runbook.schema.json
│   │   ├── l2_differentialprivacy-apply.schema.json
│   │   ├── l2_evaluation-harness.schema.json
│   │   ├── l2_execution-certificate.schema.json
│   │   ├── l2_experiment-tracking.schema.json
│   │   ├── l2_glyphser-kernel-v3.22-os.schema.json
│   │   ├── l2_model-registry.schema.json
│   │   ├── l2_modelir-executor.schema.json
│   │   ├── l2_monitoring-policy.schema.json
│   │   ├── l2_pipeline-orchestrator.schema.json
│   │   ├── l2_replay-determinism.schema.json
│   │   ├── l2_run-commit-wal.schema.json
│   │   ├── l2_security-compliance-profile.schema.json
│   │   ├── l2_tmmu-allocation.schema.json
│   │   ├── l2_trace-sidecar.schema.json
│   │   ├── l3_compatibility-test-matrix.schema.json
│   │   ├── l3_conformance-ci-pipeline.schema.json
│   │   ├── l3_conformance-harness-guide.schema.json
│   │   ├── l3_coverage-targets.schema.json
│   │   ├── l3_data-contract-fuzzing-guide.schema.json
│   │   ├── l3_failure-injection-index.schema.json
│   │   ├── l3_failure-injection-scenarios.schema.json
│   │   ├── l3_game-day-scenarios.schema.json
│   │   ├── l3_integration-test-matrix.schema.json
│   │   ├── l3_performance-plan.schema.json
│   │   ├── l3_release-gates.schema.json
│   │   ├── l3_storage-recovery-test-matrix.schema.json
│   │   ├── l3_test-plan.schema.json
│   │   ├── l3_test-vectors-catalog.schema.json
│   │   ├── l3_test_plan.schema.json
│   │   ├── l4_api-lifecycle-and-deprecation-policy.schema.json
│   │   ├── l4_architecture-decisions-log.schema.json
│   │   ├── l4_artifact-store-adapter-guide.schema.json
│   │   ├── l4_backend-adapter-guide.schema.json
│   │   ├── l4_backend-feature-matrix.schema.json
│   │   ├── l4_benchmark-evidence-spec.schema.json
│   │   ├── l4_brownfield-deployment-guide.schema.json
│   │   ├── l4_build-and-ci-matrix.schema.json
│   │   ├── l4_canonical-hashing-reference.schema.json
│   │   ├── l4_change-control-playbook.schema.json
│   │   ├── l4_cli-command-profiles.schema.json
│   │   ├── l4_code-generation-mapping.schema.json
│   │   ├── l4_coding-standards.schema.json
│   │   ├── l4_command-reference.schema.json
│   │   ├── l4_common-pitfalls-guide.schema.json
│   │   ├── l4_community-governance-model.schema.json
│   │   ├── l4_contracts-artifact-lifecycle.schema.json
│   │   ├── l4_contributing-workflow.schema.json
│   │   ├── l4_debugging-playbook.schema.json
│   │   ├── l4_determinism-audit-playbook.schema.json
│   │   ├── l4_determinism-debug-checklist.schema.json
│   │   ├── l4_deterministic-rng-implementation-guide.schema.json
│   │   ├── l4_developer-setup.schema.json
│   │   ├── l4_developer-troubleshooting-faq.schema.json
│   │   ├── l4_disaster-recovery-operations-runbook.schema.json
│   │   ├── l4_distributed-failure-recovery-guide.schema.json
│   │   ├── l4_ecosystem-expansion-roadmap.schema.json
│   │   ├── l4_eqc-ci-policy.schema.json
│   │   ├── l4_evidence-catalog.schema.json
│   │   ├── l4_expansion-catalog-041-250.schema.json
│   │   ├── l4_external-interface-standard.schema.json
│   │   ├── l4_fixtures-and-golden-data.schema.json
│   │   ├── l4_formal-verification-roadmap.schema.json
│   │   ├── l4_gentle-introduction.schema.json
│   │   ├── l4_hello-world-end-to-end-example.schema.json
│   │   ├── l4_implementation-backlog.schema.json
│   │   ├── l4_implementation-roadmap.schema.json
│   │   ├── l4_incident-postmortem-template.schema.json
│   │   ├── l4_industry-productization-upgrade-plan.schema.json
│   │   ├── l4_interoperability-standards-bridge.schema.json
│   │   ├── l4_local-replay-runbook.schema.json
│   │   ├── l4_migration-execution-guide.schema.json
│   │   ├── l4_module-scaffolding-guide.schema.json
│   │   ├── l4_operator-conformance-matrix.schema.json
│   │   ├── l4_operator-registry-cbor-contract.schema.json
│   │   ├── l4_operator-sdk-scaffold-template.schema.json
│   │   ├── l4_pr-review-checklist.schema.json
│   │   ├── l4_profiling-and-optimization-guide.schema.json
│   │   ├── l4_reference-implementations.schema.json
│   │   ├── l4_reference-stack-minimal.schema.json
│   │   ├── l4_release-evidence-assembler.schema.json
│   │   ├── l4_repo-layout-and-interfaces.schema.json
│   │   ├── l4_research-extensions-roadmap.schema.json
│   │   ├── l4_runtime-state-machine-reference.schema.json
│   │   ├── l4_schema-evolution-playbook.schema.json
│   │   ├── l4_scope-and-non-goals.schema.json
│   │   ├── l4_sdk-usage-guide.schema.json
│   │   ├── l4_security-case-template.schema.json
│   │   ├── l4_security-coding-checklist.schema.json
│   │   ├── l4_spec-lint-implementation.schema.json
│   │   ├── l4_spec-lint-rules.schema.json
│   │   ├── l4_sre-incident-triage-playbook.schema.json
│   │   ├── l4_test-harness-implementation.schema.json
│   │   ├── l4_third-party-operator-certification-program.schema.json
│   │   ├── l4_threat-model-and-control-crosswalk.schema.json
│   │   ├── l4_tooling-and-automation-suite.schema.json
│   │   └── l4_tooling-suite.schema.json
│   ├── contract_schema_meta.json
│   ├── l3_operator_error_vectors.schema.json
│   ├── l3_operator_vectors.schema.json
│   ├── SCHEMA_CONVENTIONS.txt
│   └── SCHEMA_FORMAT_DECISION.txt
├── scripts
│   ├── repro
│   │   └── host_meta.py
│   └── run_hello_core.py
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
│       ├── import
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
├── temp
│   ├── checkpoint-restore
│   │   └── ckpt-1.json
│   └── RESUME CODEX
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
│   ├── conformance
│   │   └── vectors
│   │       ├── interface_hash
│   │       │   └── vectors.json
│   │       ├── operator_stub
│   │       ├── operators
│   │       │   ├── Glyphser_Backend_LoadDriver.json
│   │       │   ├── Glyphser_Certificate_EvidenceValidate.json
│   │       │   ├── Glyphser_Checkpoint_CheckpointMigrate.json
│   │       │   ├── Glyphser_Checkpoint_Restore.json
│   │       │   ├── Glyphser_Config_ManifestMigrate.json
│   │       │   ├── Glyphser_Data_NextBatch.json
│   │       │   ├── Glyphser_DifferentialPrivacy_Apply.json
│   │       │   ├── Glyphser_Error_Emit.json
│   │       │   ├── Glyphser_Import_LegacyFramework.json
│   │       │   ├── Glyphser_IO_SaveCheckpoint.json
│   │       │   ├── Glyphser_Model_Forward.json
│   │       │   ├── Glyphser_Model_ModelIR_Executor.json
│   │       │   ├── Glyphser_Monitor_DriftCompute.json
│   │       │   ├── Glyphser_Monitor_Emit.json
│   │       │   ├── Glyphser_Monitor_Register.json
│   │       │   ├── Glyphser_Registry_StageTransition.json
│   │       │   ├── Glyphser_Registry_VersionCreate.json
│   │       │   ├── Glyphser_TMMU_PrepareMemory.json
│   │       │   ├── Glyphser_Trace_TraceMigrate.json
│   │       │   ├── Glyphser_Tracking_ArtifactGet.json
│   │       │   ├── Glyphser_Tracking_ArtifactList.json
│   │       │   ├── Glyphser_Tracking_ArtifactPut.json
│   │       │   ├── Glyphser_Tracking_ArtifactTombstone.json
│   │       │   ├── Glyphser_Tracking_MetricLog.json
│   │       │   ├── Glyphser_Tracking_RunCreate.json
│   │       │   ├── Glyphser_Tracking_RunEnd.json
│   │       │   └── Glyphser_Tracking_RunStart.json
│   │       └── storage
│   │           └── state_recovery_vectors.json
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
│   │   └── test_observability_gate.py
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
├── tools
│   ├── codegen
│   │   ├── templates
│   │   │   ├── bindings.py.tpl
│   │   │   ├── error.py.tpl
│   │   │   ├── models.py.tpl
│   │   │   ├── operators.py.tpl
│   │   │   └── validators.py.tpl
│   │   ├── check_generated_drift.py
│   │   ├── clean_build.py
│   │   ├── clean_build_generate.py
│   │   ├── diff_fidelity.py
│   │   ├── generate.py
│   │   ├── input_hash_manifest.py
│   │   └── run_and_test.py
│   ├── conformance
│   │   ├── __init__.py
│   │   ├── cli.py
│   │   └── report_template.json
│   ├── deploy
│   │   ├── overlays
│   │   │   ├── dev.json
│   │   │   ├── prod.json
│   │   │   └── staging.json
│   │   ├── templates
│   │   │   ├── policy_bindings.json.tpl
│   │   │   └── runtime_config.json.tpl
│   │   ├── deploy_rollback_gate.py
│   │   ├── generate_bundle.py
│   │   ├── generate_env_manifest.py
│   │   ├── generate_migration_plan.py
│   │   ├── generate_overlays.py
│   │   ├── run_deployment_pipeline.py
│   │   └── validate_profile.py
│   ├── api_cli.py
│   ├── api_contract_gate.py
│   ├── build_operator_registry.py
│   ├── build_release_bundle.py
│   ├── conformance_cli.py
│   ├── coverage_report.py
│   ├── doc_code_separation_gate.py
│   ├── error_code_gate.py
│   ├── external_validation_gate.py
│   ├── fixtures_gate.py
│   ├── ga_release_gate.py
│   ├── materialize_doc_artifacts.py
│   ├── merge_markdown_to_txt.py
│   ├── observability_gate.py
│   ├── operator_vectors.py
│   ├── push_button.py
│   ├── registry_gate.py
│   ├── release_evidence_gate.py
│   ├── reproducibility_check.py
│   ├── schema_gate.py
│   ├── security_artifacts.py
│   ├── security_baseline_gate.py
│   ├── spec_lint.py
│   ├── state_recovery_gate.py
│   ├── validate_data_integrity.py
│   ├── vector_gate.py
│   ├── verify_doc_artifacts.py
│   └── verify_release.py
├── vectors
│   ├── checkpoint-restore
│   │   ├── vectors-manifest.json
│   │   └── vectors.json
│   ├── failure-injection
│   │   ├── vectors-manifest.json
│   │   └── vectors.json
│   ├── hello-core
│   │   ├── vectors-manifest.json
│   │   └── vectors.json
│   ├── perf-scale
│   │   ├── vectors-manifest.json
│   │   └── vectors.json
│   ├── registry-lifecycle
│   │   ├── vectors-manifest.json
│   │   └── vectors.json
│   ├── replay-determinism
│   │   ├── vectors-manifest.json
│   │   └── vectors.json
│   ├── replay-suite-1
│   │   ├── vectors-manifest.json
│   │   └── vectors.json
│   ├── replay-suites
│   │   └── index.json
│   ├── tracking-monitoring
│   │   ├── vectors-manifest.json
│   │   └── vectors.json
│   └── catalog.json
├── .gitignore
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── data-registry.yaml
├── Dockerfile
├── ecosystem-compatibility-aggregate.yaml
├── ecosystem-graph.yaml
├── ecosystem-registry.yaml
├── ecosystem-validation-log.md
├── ecosystem.md
├── LICENSE
├── migration-plan-template.yaml
├── milestones.txt
├── portfolio-release-notes-template.md
├── pyproject.toml
├── README.md
├── RELEASE_NOTES_v0.1.0.md
├── requirements.lock
├── SECURITY.md
├── semantic_lint_high_confidence.txt
├── semantic_lint_report.txt
└── VERSIONING.md
```

## File Purpose Catalog
| File | Purpose |
|---|---|
| `.github/workflows/conformance-gate.yml` | CI workflow definition for `conformance-gate` automation. |
| `.github/workflows/push-button.yml` | CI workflow definition for `push-button` automation. |
| `.github/workflows/registry-gate.yml` | CI workflow definition for `registry-gate` automation. |
| `.github/workflows/schema-gate.yml` | CI workflow definition for `schema-gate` automation. |
| `.gitignore` | Root-level project artifact `.gitignore` used by repository workflows. |
| `CODE_OF_CONDUCT.md` | Community behavior and conduct policy. |
| `CONTRIBUTING.md` | Contribution workflow and developer contribution requirements. |
| `Dockerfile` | Root-level project artifact `Dockerfile` used by repository workflows. |
| `LICENSE` | Root-level project artifact `LICENSE` used by repository workflows. |
| `README.md` | Primary project overview and quick start entry point. |
| `RELEASE_NOTES_v0.1.0.md` | Release notes for version v0.1.0. |
| `SECURITY.md` | Security reporting policy and contact process. |
| `VERSIONING.md` | Versioning and compatibility policy reference. |
| `assets/glyphser3.png` | Static project asset `glyphser3.png`. |
| `assets/glyphser3.svg` | Static project asset `glyphser3.svg`. |
| `conformance/.gitkeep` | Conformance artifact for `.gitkeep` execution/reporting. |
| `evidence/conformance/reports/latest.json` | Conformance artifact for `latest` execution/reporting. |
| `evidence/conformance/results/latest.json` | Conformance artifact for `latest` execution/reporting. |
| `conformance/artifacts/inputs/vectors/canonical_cbor/.gitkeep` | Conformance artifact for `.gitkeep` execution/reporting. |
| `conformance/artifacts/inputs/vectors/canonical_cbor/vectors.json` | Conformance artifact for `vectors` execution/reporting. |
| `conformance/artifacts/inputs/vectors/interface_hash/.gitkeep` | Conformance artifact for `.gitkeep` execution/reporting. |
| `conformance/artifacts/inputs/vectors/interface_hash/vectors.json` | Conformance artifact for `vectors` execution/reporting. |
| `conformance/artifacts/inputs/vectors/struct_validation/.gitkeep` | Conformance artifact for `.gitkeep` execution/reporting. |
| `conformance/artifacts/inputs/vectors/struct_validation/vectors.json` | Conformance artifact for `vectors` execution/reporting. |
| `contracts/capability_catalog.cbor` | Machine-readable contract/interface artifact for `capability catalog`. |
| `contracts/catalog-manifest.json` | Machine-readable contract/interface artifact for `catalog manifest`. |
| `contracts/digest_catalog.cbor` | Machine-readable contract/interface artifact for `digest catalog`. |
| `contracts/error_codes.cbor` | Machine-readable contract/interface artifact for `error codes`. |
| `contracts/error_codes.json` | Machine-readable contract/interface artifact for `error codes`. |
| `contracts/interface_hash.json` | Machine-readable contract/interface artifact for `interface hash`. |
| `contracts/openapi_public_api_v1.yaml` | Machine-readable contract/interface artifact for `openapi public api v1`. |
| `contracts/operator_registry.cbor` | Machine-readable contract/interface artifact for `operator registry`. |
| `contracts/operator_registry.json` | Machine-readable contract/interface artifact for `operator registry`. |
| `contracts/operator_registry_source.json` | Machine-readable contract/interface artifact for `operator registry source`. |
| `contracts/schema_catalog.cbor` | Machine-readable contract/interface artifact for `schema catalog`. |
| `contracts/vectors_catalog.cbor` | Machine-readable contract/interface artifact for `vectors catalog`. |
| `data-registry.yaml` | Root-level project artifact `data-registry.yaml` used by repository workflows. |
| `artifacts/bundles/hello-core-bundle.sha256` | Release distribution artifact `hello-core-bundle.sha256` used for publish/verification. |
| `artifacts/bundles/hello-core-bundle.tar.gz` | Release distribution artifact `hello-core-bundle.tar.gz` used for publish/verification. |
| `docs/BRAND.md` | Documentation artifact describing `BRAND`. |
| `docs/HELLO_CORE_NEXT_STEPS.md` | Documentation artifact describing `HELLO CORE NEXT STEPS`. |
| `docs/INTERPRETATION_LOG.md` | Documentation artifact describing `INTERPRETATION LOG`. |
| `docs/START-HERE.md` | Documentation artifact describing `START HERE`. |
| `docs/VERIFY.md` | Documentation artifact describing `VERIFY`. |
| `docs/WEEKLY_REVIEW_TEMPLATE.md` | Documentation artifact describing `WEEKLY REVIEW TEMPLATE`. |
| `docs/business/DELIVERABLES_LIST.md` | Documentation artifact describing `DELIVERABLES LIST`. |
| `docs/business/FEES.md` | Documentation artifact describing `FEES`. |
| `docs/business/LOCAL_NETWORK.md` | Documentation artifact describing `LOCAL NETWORK`. |
| `docs/business/OFFERS.md` | Documentation artifact describing `OFFERS`. |
| `docs/business/STRUCTURE_TRACK.md` | Documentation artifact describing `STRUCTURE TRACK`. |
| `docs/compatibility/CERTIFICATION_DELIVERABLES.md` | Documentation artifact describing `CERTIFICATION DELIVERABLES`. |
| `docs/compatibility/COMPATIBILITY_CRITERIA_v0.1.md` | Documentation artifact describing `COMPATIBILITY CRITERIA v0.1`. |
| `docs/compatibility/VENDOR_SELF_TEST_KIT.md` | Documentation artifact describing `VENDOR SELF TEST KIT`. |
| `docs/contracts/COMPATIBILITY_POLICY.md` | Documentation artifact describing `COMPATIBILITY POLICY`. |
| `docs/contracts/CONFORMANCE_SUITE_v0.1.md` | Documentation artifact describing `CONFORMANCE SUITE v0.1`. |
| `docs/contracts/DETERMINISM_PROFILE_v0.1.md` | Documentation artifact describing `DETERMINISM PROFILE v0.1`. |
| `docs/contracts/ERROR_CODES.md` | Documentation artifact describing `ERROR CODES`. |
| `docs/contracts/NUMERIC_POLICY_v0.1.md` | Documentation artifact describing `NUMERIC POLICY v0.1`. |
| `docs/examples/hello-core/hello-core-golden.json` | Documentation artifact describing `hello core golden`. |
| `docs/examples/hello-core/manifest.core.yaml` | Documentation artifact describing `manifest.core`. |
| `docs/examples/operators/Glyphser_Backend_LoadDriver.json` | Documentation artifact describing `Glyphser Backend LoadDriver`. |
| `docs/examples/operators/Glyphser_Certificate_EvidenceValidate.json` | Documentation artifact describing `Glyphser Certificate EvidenceValidate`. |
| `docs/examples/operators/Glyphser_Checkpoint_CheckpointMigrate.json` | Documentation artifact describing `Glyphser Checkpoint CheckpointMigrate`. |
| `docs/examples/operators/Glyphser_Checkpoint_Restore.json` | Documentation artifact describing `Glyphser Checkpoint Restore`. |
| `docs/examples/operators/Glyphser_Config_ManifestMigrate.json` | Documentation artifact describing `Glyphser Config ManifestMigrate`. |
| `docs/examples/operators/Glyphser_Data_NextBatch.json` | Documentation artifact describing `Glyphser Data NextBatch`. |
| `docs/examples/operators/Glyphser_DifferentialPrivacy_Apply.json` | Documentation artifact describing `Glyphser DifferentialPrivacy Apply`. |
| `docs/examples/operators/Glyphser_Error_Emit.json` | Documentation artifact describing `Glyphser Error Emit`. |
| `docs/examples/operators/Glyphser_IO_SaveCheckpoint.json` | Documentation artifact describing `Glyphser IO SaveCheckpoint`. |
| `docs/examples/operators/Glyphser_Import_LegacyFramework.json` | Documentation artifact describing `Glyphser Import LegacyFramework`. |
| `docs/examples/operators/Glyphser_Model_Forward.json` | Documentation artifact describing `Glyphser Model Forward`. |
| `docs/examples/operators/Glyphser_Model_ModelIR_Executor.json` | Documentation artifact describing `Glyphser Model ModelIR Executor`. |
| `docs/examples/operators/Glyphser_Monitor_DriftCompute.json` | Documentation artifact describing `Glyphser Monitor DriftCompute`. |
| `docs/examples/operators/Glyphser_Monitor_Emit.json` | Documentation artifact describing `Glyphser Monitor Emit`. |
| `docs/examples/operators/Glyphser_Monitor_Register.json` | Documentation artifact describing `Glyphser Monitor Register`. |
| `docs/examples/operators/Glyphser_Registry_StageTransition.json` | Documentation artifact describing `Glyphser Registry StageTransition`. |
| `docs/examples/operators/Glyphser_Registry_VersionCreate.json` | Documentation artifact describing `Glyphser Registry VersionCreate`. |
| `docs/examples/operators/Glyphser_TMMU_PrepareMemory.json` | Documentation artifact describing `Glyphser TMMU PrepareMemory`. |
| `docs/examples/operators/Glyphser_Trace_TraceMigrate.json` | Documentation artifact describing `Glyphser Trace TraceMigrate`. |
| `docs/examples/operators/Glyphser_Tracking_ArtifactGet.json` | Documentation artifact describing `Glyphser Tracking ArtifactGet`. |
| `docs/examples/operators/Glyphser_Tracking_ArtifactList.json` | Documentation artifact describing `Glyphser Tracking ArtifactList`. |
| `docs/examples/operators/Glyphser_Tracking_ArtifactPut.json` | Documentation artifact describing `Glyphser Tracking ArtifactPut`. |
| `docs/examples/operators/Glyphser_Tracking_ArtifactTombstone.json` | Documentation artifact describing `Glyphser Tracking ArtifactTombstone`. |
| `docs/examples/operators/Glyphser_Tracking_MetricLog.json` | Documentation artifact describing `Glyphser Tracking MetricLog`. |
| `docs/examples/operators/Glyphser_Tracking_RunCreate.json` | Documentation artifact describing `Glyphser Tracking RunCreate`. |
| `docs/examples/operators/Glyphser_Tracking_RunEnd.json` | Documentation artifact describing `Glyphser Tracking RunEnd`. |
| `docs/examples/operators/Glyphser_Tracking_RunStart.json` | Documentation artifact describing `Glyphser Tracking RunStart`. |
| `docs/how_to/MILESTONE_15_TWO_HOST_RUNBOOK.md` | Documentation artifact describing `MILESTONE 15 TWO HOST RUNBOOK`. |
| `docs/ip/BADGE_PROGRAM_DRAFT.md` | Documentation artifact describing `BADGE PROGRAM DRAFT`. |
| `docs/ip/DEFENSIVE_PUBLICATION_PLAN.md` | Documentation artifact describing `DEFENSIVE PUBLICATION PLAN`. |
| `docs/ip/DISCLOSURE-RULES.md` | Documentation artifact describing `DISCLOSURE RULES`. |
| `docs/ip/IP-POSTURE.md` | Documentation artifact describing `IP POSTURE`. |
| `docs/layer1-foundation/API-Interfaces.md` | Documentation artifact describing `API Interfaces`. |
| `docs/layer1-foundation/Canonical-CBOR-Profile.md` | Documentation artifact describing `Canonical CBOR Profile`. |
| `docs/layer1-foundation/Data-Structures.md` | Documentation artifact describing `Data Structures`. |
| `docs/layer1-foundation/Dependency-Lock-Policy.md` | Documentation artifact describing `Dependency Lock Policy`. |
| `docs/layer1-foundation/Determinism-Profiles.md` | Documentation artifact describing `Determinism Profiles`. |
| `docs/layer1-foundation/Digest-Catalog.md` | Documentation artifact describing `Digest Catalog`. |
| `docs/layer1-foundation/Environment-Manifest.md` | Documentation artifact describing `Environment Manifest`. |
| `docs/layer1-foundation/Error-Codes.md` | Documentation artifact describing `Error Codes`. |
| `docs/layer1-foundation/Normativity-Legend.md` | Documentation artifact describing `Normativity Legend`. |
| `docs/layer1-foundation/Operator-Registry-Schema.md` | Documentation artifact describing `Operator Registry Schema`. |
| `docs/layer1-foundation/Redaction-Policy.md` | Documentation artifact describing `Redaction Policy`. |
| `docs/layer2-specs/AuthZ-Capability-Matrix.md` | Documentation artifact describing `AuthZ Capability Matrix`. |
| `docs/layer2-specs/Checkpoint-Schema.md` | Documentation artifact describing `Checkpoint Schema`. |
| `docs/layer2-specs/Config-Schema.md` | Documentation artifact describing `Config Schema`. |
| `docs/layer2-specs/Data-Lineage.md` | Documentation artifact describing `Data Lineage`. |
| `docs/layer2-specs/Data-NextBatch.md` | Documentation artifact describing `Data NextBatch`. |
| `docs/layer2-specs/Deployment-Runbook.md` | Documentation artifact describing `Deployment Runbook`. |
| `docs/layer2-specs/DifferentialPrivacy-Apply.md` | Documentation artifact describing `DifferentialPrivacy Apply`. |
| `docs/layer2-specs/Evaluation-Harness.md` | Documentation artifact describing `Evaluation Harness`. |
| `docs/layer2-specs/Execution-Certificate.md` | Documentation artifact describing `Execution Certificate`. |
| `docs/layer2-specs/Experiment-Tracking.md` | Documentation artifact describing `Experiment Tracking`. |
| `docs/layer2-specs/Glyphser-Kernel-v3.22-OS.md` | Documentation artifact describing `Glyphser Kernel v3.22 OS`. |
| `docs/layer2-specs/Model-Registry.md` | Documentation artifact describing `Model Registry`. |
| `docs/layer2-specs/ModelIR-Executor.md` | Documentation artifact describing `ModelIR Executor`. |
| `docs/layer2-specs/Monitoring-Policy.md` | Documentation artifact describing `Monitoring Policy`. |
| `docs/layer2-specs/Pipeline-Orchestrator.md` | Documentation artifact describing `Pipeline Orchestrator`. |
| `docs/layer2-specs/Replay-Determinism.md` | Documentation artifact describing `Replay Determinism`. |
| `docs/layer2-specs/Run-Commit-WAL.md` | Documentation artifact describing `Run Commit WAL`. |
| `docs/layer2-specs/Security-Compliance-Profile.md` | Documentation artifact describing `Security Compliance Profile`. |
| `docs/layer2-specs/TMMU-Allocation.md` | Documentation artifact describing `TMMU Allocation`. |
| `docs/layer2-specs/Trace-Sidecar.md` | Documentation artifact describing `Trace Sidecar`. |
| `docs/layer3-tests/Compatibility-Test-Matrix.md` | Documentation artifact describing `Compatibility Test Matrix`. |
| `docs/layer3-tests/Conformance-CI-Pipeline.md` | Documentation artifact describing `Conformance CI Pipeline`. |
| `docs/layer3-tests/Conformance-Harness-Guide.md` | Documentation artifact describing `Conformance Harness Guide`. |
| `docs/layer3-tests/Coverage-Targets.md` | Documentation artifact describing `Coverage Targets`. |
| `docs/layer3-tests/Data-Contract-Fuzzing-Guide.md` | Documentation artifact describing `Data Contract Fuzzing Guide`. |
| `docs/layer3-tests/Failure-Injection-Index.md` | Documentation artifact describing `Failure Injection Index`. |
| `docs/layer3-tests/Failure-Injection-Scenarios.md` | Documentation artifact describing `Failure Injection Scenarios`. |
| `docs/layer3-tests/Game-Day-Scenarios.md` | Documentation artifact describing `Game Day Scenarios`. |
| `docs/layer3-tests/Integration-Test-Matrix.md` | Documentation artifact describing `Integration Test Matrix`. |
| `docs/layer3-tests/Operator-Vectors.md` | Documentation artifact describing `Operator Vectors`. |
| `docs/layer3-tests/Performance-Plan.md` | Documentation artifact describing `Performance Plan`. |
| `docs/layer3-tests/Release-Gates.md` | Documentation artifact describing `Release Gates`. |
| `docs/layer3-tests/Storage-Recovery-Test-Matrix.md` | Documentation artifact describing `Storage Recovery Test Matrix`. |
| `docs/layer3-tests/Test-Coverage-Gaps.md` | Documentation artifact describing `Test Coverage Gaps`. |
| `docs/layer3-tests/Test-Inventory.md` | Documentation artifact describing `Test Inventory`. |
| `docs/layer3-tests/Test-Plan.md` | Documentation artifact describing `Test Plan`. |
| `docs/layer3-tests/Test-Vectors-Catalog.md` | Documentation artifact describing `Test Vectors Catalog`. |
| `docs/layer4-implementation/API-Lifecycle-and-Deprecation-Policy.md` | Documentation artifact describing `API Lifecycle and Deprecation Policy`. |
| `docs/layer4-implementation/Algorithm-Closure.md` | Documentation artifact describing `Algorithm Closure`. |
| `docs/layer4-implementation/Architecture-Decisions-Log.md` | Documentation artifact describing `Architecture Decisions Log`. |
| `docs/layer4-implementation/Artifact-Store-Adapter-Guide.md` | Documentation artifact describing `Artifact Store Adapter Guide`. |
| `docs/layer4-implementation/Backend-Adapter-Guide.md` | Documentation artifact describing `Backend Adapter Guide`. |
| `docs/layer4-implementation/Backend-Feature-Matrix.md` | Documentation artifact describing `Backend Feature Matrix`. |
| `docs/layer4-implementation/Benchmark-Evidence-Spec.md` | Documentation artifact describing `Benchmark Evidence Spec`. |
| `docs/layer4-implementation/Brownfield-Deployment-Guide.md` | Documentation artifact describing `Brownfield Deployment Guide`. |
| `docs/layer4-implementation/Build-and-CI-Matrix.md` | Documentation artifact describing `Build and CI Matrix`. |
| `docs/layer4-implementation/CLI-Command-Profiles.md` | Documentation artifact describing `CLI Command Profiles`. |
| `docs/layer4-implementation/Canonical-Hashing-Reference.md` | Documentation artifact describing `Canonical Hashing Reference`. |
| `docs/layer4-implementation/Change-Control-Playbook.md` | Documentation artifact describing `Change Control Playbook`. |
| `docs/layer4-implementation/Code-Generation-Mapping.md` | Documentation artifact describing `Code Generation Mapping`. |
| `docs/layer4-implementation/Coding-Standards.md` | Documentation artifact describing `Coding Standards`. |
| `docs/layer4-implementation/Command-Reference.md` | Documentation artifact describing `Command Reference`. |
| `docs/layer4-implementation/Common-Pitfalls-Guide.md` | Documentation artifact describing `Common Pitfalls Guide`. |
| `docs/layer4-implementation/Community-Governance-Model.md` | Documentation artifact describing `Community Governance Model`. |
| `docs/layer4-implementation/Contracts-Artifact-Lifecycle.md` | Documentation artifact describing `Contracts Artifact Lifecycle`. |
| `docs/layer4-implementation/Contributing-Workflow.md` | Documentation artifact describing `Contributing Workflow`. |
| `docs/layer4-implementation/Debugging-Playbook.md` | Documentation artifact describing `Debugging Playbook`. |
| `docs/layer4-implementation/Deployment-Generation-Profile.md` | Documentation artifact describing `Deployment Generation Profile`. |
| `docs/layer4-implementation/Determinism-Audit-Playbook.md` | Documentation artifact describing `Determinism Audit Playbook`. |
| `docs/layer4-implementation/Determinism-Debug-Checklist.md` | Documentation artifact describing `Determinism Debug Checklist`. |
| `docs/layer4-implementation/Deterministic-RNG-Implementation-Guide.md` | Documentation artifact describing `Deterministic RNG Implementation Guide`. |
| `docs/layer4-implementation/Developer-Setup.md` | Documentation artifact describing `Developer Setup`. |
| `docs/layer4-implementation/Developer-Troubleshooting-FAQ.md` | Documentation artifact describing `Developer Troubleshooting FAQ`. |
| `docs/layer4-implementation/Disaster-Recovery-Operations-Runbook.md` | Documentation artifact describing `Disaster Recovery Operations Runbook`. |
| `docs/layer4-implementation/Distributed-Failure-Recovery-Guide.md` | Documentation artifact describing `Distributed Failure Recovery Guide`. |
| `docs/layer4-implementation/EQC-CI-Policy.md` | Documentation artifact describing `EQC CI Policy`. |
| `docs/layer4-implementation/Ecosystem-Expansion-Roadmap.md` | Documentation artifact describing `Ecosystem Expansion Roadmap`. |
| `docs/layer4-implementation/Evidence-Catalog.md` | Documentation artifact describing `Evidence Catalog`. |
| `docs/layer4-implementation/Expansion-Catalog-041-250.md` | Documentation artifact describing `Expansion Catalog 041 250`. |
| `docs/layer4-implementation/External-Interface-Standard.md` | Documentation artifact describing `External Interface Standard`. |
| `docs/layer4-implementation/Fixtures-and-Golden-Data.md` | Documentation artifact describing `Fixtures and Golden Data`. |
| `docs/layer4-implementation/Formal-Verification-Roadmap.md` | Documentation artifact describing `Formal Verification Roadmap`. |
| `docs/layer4-implementation/Gentle-Introduction.md` | Documentation artifact describing `Gentle Introduction`. |
| `docs/layer4-implementation/Hello-World-End-to-End-Example.md` | Documentation artifact describing `Hello World End to End Example`. |
| `docs/layer4-implementation/Implementation-Backlog.md` | Documentation artifact describing `Implementation Backlog`. |
| `docs/layer4-implementation/Implementation-Roadmap.md` | Documentation artifact describing `Implementation Roadmap`. |
| `docs/layer4-implementation/Incident-Postmortem-Template.md` | Documentation artifact describing `Incident Postmortem Template`. |
| `docs/layer4-implementation/Industry-Productization-Upgrade-Plan.md` | Documentation artifact describing `Industry Productization Upgrade Plan`. |
| `docs/layer4-implementation/Interoperability-Standards-Bridge.md` | Documentation artifact describing `Interoperability Standards Bridge`. |
| `docs/layer4-implementation/Local-Replay-Runbook.md` | Documentation artifact describing `Local Replay Runbook`. |
| `docs/layer4-implementation/Migration-Execution-Guide.md` | Documentation artifact describing `Migration Execution Guide`. |
| `docs/layer4-implementation/Module-Scaffolding-Guide.md` | Documentation artifact describing `Module Scaffolding Guide`. |
| `docs/layer4-implementation/Operator-Conformance-Matrix.md` | Documentation artifact describing `Operator Conformance Matrix`. |
| `docs/layer4-implementation/Operator-Readiness-Checklist.md` | Documentation artifact describing `Operator Readiness Checklist`. |
| `docs/layer4-implementation/Operator-Registry-CBOR-Contract.md` | Documentation artifact describing `Operator Registry CBOR Contract`. |
| `docs/layer4-implementation/Operator-SDK-Scaffold-Template.md` | Documentation artifact describing `Operator SDK Scaffold Template`. |
| `docs/layer4-implementation/PR-Review-Checklist.md` | Documentation artifact describing `PR Review Checklist`. |
| `docs/layer4-implementation/Profiling-and-Optimization-Guide.md` | Documentation artifact describing `Profiling and Optimization Guide`. |
| `docs/layer4-implementation/Reference-Implementations.md` | Documentation artifact describing `Reference Implementations`. |
| `docs/layer4-implementation/Reference-Stack-Minimal.md` | Documentation artifact describing `Reference Stack Minimal`. |
| `docs/layer4-implementation/Release-Evidence-Assembler.md` | Documentation artifact describing `Release Evidence Assembler`. |
| `docs/layer4-implementation/Repo-Layout-and-Interfaces.md` | Documentation artifact describing `Repo Layout and Interfaces`. |
| `docs/layer4-implementation/Research-Extensions-Roadmap.md` | Documentation artifact describing `Research Extensions Roadmap`. |
| `docs/layer4-implementation/Runtime-State-Machine-Reference.md` | Documentation artifact describing `Runtime State Machine Reference`. |
| `docs/layer4-implementation/SDK-Usage-Guide.md` | Documentation artifact describing `SDK Usage Guide`. |
| `docs/layer4-implementation/SRE-Incident-Triage-Playbook.md` | Documentation artifact describing `SRE Incident Triage Playbook`. |
| `docs/layer4-implementation/Schema-Evolution-Playbook.md` | Documentation artifact describing `Schema Evolution Playbook`. |
| `docs/layer4-implementation/Scope-and-Non-Goals.md` | Documentation artifact describing `Scope and Non Goals`. |
| `docs/layer4-implementation/Security-Case-Template.md` | Documentation artifact describing `Security Case Template`. |
| `docs/layer4-implementation/Security-Coding-Checklist.md` | Documentation artifact describing `Security Coding Checklist`. |
| `docs/layer4-implementation/Spec-Lint-Implementation.md` | Documentation artifact describing `Spec Lint Implementation`. |
| `docs/layer4-implementation/Spec-Lint-Rules.md` | Documentation artifact describing `Spec Lint Rules`. |
| `docs/layer4-implementation/Target-Architecture-Profile.md` | Documentation artifact describing `Target Architecture Profile`. |
| `docs/layer4-implementation/Test-Harness-Implementation.md` | Documentation artifact describing `Test Harness Implementation`. |
| `docs/layer4-implementation/Third-Party-Operator-Certification-Program.md` | Documentation artifact describing `Third Party Operator Certification Program`. |
| `docs/layer4-implementation/Threat-Model-and-Control-Crosswalk.md` | Documentation artifact describing `Threat Model and Control Crosswalk`. |
| `docs/layer4-implementation/Tooling-Suite.md` | Documentation artifact describing `Tooling Suite`. |
| `docs/layer4-implementation/Tooling-and-Automation-Suite.md` | Documentation artifact describing `Tooling and Automation Suite`. |
| `docs/ops/DEPLOYMENT_RUNBOOK.md` | Documentation artifact describing `DEPLOYMENT RUNBOOK`. |
| `docs/ops/INCIDENT_RESPONSE.md` | Documentation artifact describing `INCIDENT RESPONSE`. |
| `docs/ops/ROLLBACK_RUNBOOK.md` | Documentation artifact describing `ROLLBACK RUNBOOK`. |
| `docs/ops/SLOs.md` | Documentation artifact describing `SLOs`. |
| `docs/product/ACCESSIBILITY_REVIEW.md` | Documentation artifact describing `ACCESSIBILITY REVIEW`. |
| `docs/product/ANNUAL_SECURITY_REVIEW_POLICY.md` | Documentation artifact describing `ANNUAL SECURITY REVIEW POLICY`. |
| `docs/product/API_CLI_COMMANDS.md` | Documentation artifact describing `API CLI COMMANDS`. |
| `docs/product/API_LIFECYCLE_POLICY.md` | Documentation artifact describing `API LIFECYCLE POLICY`. |
| `docs/product/API_REFERENCE_v1.md` | Documentation artifact describing `API REFERENCE v1`. |
| `docs/product/API_STYLE_GUIDE.md` | Documentation artifact describing `API STYLE GUIDE`. |
| `docs/product/CHANGE_COMMUNICATION_SLA.md` | Documentation artifact describing `CHANGE COMMUNICATION SLA`. |
| `docs/product/COMPLIANCE_EVIDENCE_INDEX.md` | Documentation artifact describing `COMPLIANCE EVIDENCE INDEX`. |
| `docs/product/DEPENDENCY_LICENSE_REVIEW.md` | Documentation artifact describing `DEPENDENCY LICENSE REVIEW`. |
| `docs/product/DOCS_VERSIONING_POLICY.md` | Documentation artifact describing `DOCS VERSIONING POLICY`. |
| `docs/product/GA_COMPATIBILITY_GUARANTEES.md` | Documentation artifact describing `GA COMPATIBILITY GUARANTEES`. |
| `docs/product/GA_CONTRACTUAL_SUPPORT_SLA.md` | Documentation artifact describing `GA CONTRACTUAL SUPPORT SLA`. |
| `docs/product/GA_GO_NO_GO_CHECKLIST.md` | Documentation artifact describing `GA GO NO GO CHECKLIST`. |
| `docs/product/GA_MIGRATION_GUIDE.md` | Documentation artifact describing `GA MIGRATION GUIDE`. |
| `docs/product/GA_RELEASE_TRAIN_POLICY.md` | Documentation artifact describing `GA RELEASE TRAIN POLICY`. |
| `docs/product/GA_SIGNOFF.md` | Documentation artifact describing `GA SIGNOFF`. |
| `docs/product/GA_STATUS_INCIDENT_COMMUNICATION.md` | Documentation artifact describing `GA STATUS INCIDENT COMMUNICATION`. |
| `docs/product/GA_SUPPORT_LIFECYCLE.md` | Documentation artifact describing `GA SUPPORT LIFECYCLE`. |
| `docs/product/GA_SUPPORT_MATRIX.md` | Documentation artifact describing `GA SUPPORT MATRIX`. |
| `docs/product/GA_SUPPORT_OPERATIONS_READINESS.md` | Documentation artifact describing `GA SUPPORT OPERATIONS READINESS`. |
| `docs/product/M17_APPROVAL.md` | Documentation artifact describing `M17 APPROVAL`. |
| `docs/product/M18_CONTRACT_TEST_REPORT.md` | Documentation artifact describing `M18 CONTRACT TEST REPORT`. |
| `docs/product/M19_RECOVERY_TEST_REPORT.md` | Documentation artifact describing `M19 RECOVERY TEST REPORT`. |
| `docs/product/M20_SECURITY_TEST_REPORT.md` | Documentation artifact describing `M20 SECURITY TEST REPORT`. |
| `docs/product/M21_DEPLOYMENT_TEST_REPORT.md` | Documentation artifact describing `M21 DEPLOYMENT TEST REPORT`. |
| `docs/product/M22_OBSERVABILITY_REPORT.md` | Documentation artifact describing `M22 OBSERVABILITY REPORT`. |
| `docs/product/M23_EXTERNAL_VALIDATION_REPORT.md` | Documentation artifact describing `M23 EXTERNAL VALIDATION REPORT`. |
| `docs/product/M24_GA_RELEASE_REPORT.md` | Documentation artifact describing `M24 GA RELEASE REPORT`. |
| `docs/product/PERSISTENCE_SCHEMA_v1.md` | Documentation artifact describing `PERSISTENCE SCHEMA v1`. |
| `docs/product/PERSISTENT_STORAGE_ADAPTER_CONTRACT.md` | Documentation artifact describing `PERSISTENT STORAGE ADAPTER CONTRACT`. |
| `docs/product/POST_GA_GOVERNANCE.md` | Documentation artifact describing `POST GA GOVERNANCE`. |
| `docs/product/PRIVACY_IMPACT_ASSESSMENT_WORKFLOW.md` | Documentation artifact describing `PRIVACY IMPACT ASSESSMENT WORKFLOW`. |
| `docs/product/PRODUCT_SCOPE.md` | Documentation artifact describing `PRODUCT SCOPE`. |
| `docs/product/RUNTIME_PROFILES.md` | Documentation artifact describing `RUNTIME PROFILES`. |
| `docs/product/SUPPLY_CHAIN_TRUST_POLICY.md` | Documentation artifact describing `SUPPLY CHAIN TRUST POLICY`. |
| `docs/release/CHECKSUMS_v0.1.0.sha256` | Documentation artifact describing `CHECKSUMS v0.1.0`. |
| `docs/release/CHECKSUMS_v0.1.0.sha256.asc` | Documentation artifact describing `CHECKSUMS v0.1.0.sha256`. |
| `docs/release/RELEASE_PUBKEY.asc` | Documentation artifact describing `RELEASE PUBKEY`. |
| `docs/release/SIGNING.md` | Documentation artifact describing `SIGNING`. |
| `docs/evidence/CONFORMANCE_REPORT_TEMPLATE.md` | Documentation artifact describing `CONFORMANCE REPORT TEMPLATE`. |
| `docs/evidence/INTEGRATION_REPORT_TEMPLATE.md` | Documentation artifact describing `INTEGRATION REPORT TEMPLATE`. |
| `docs/evidence/OUTREACH_2026-02-27.md` | Documentation artifact describing `OUTREACH 2026 02 27`. |
| `docs/evidence/merged_docs.txt` | Documentation artifact describing `merged docs`. |
| `docs/security/OPERATIONS.md` | Documentation artifact describing `OPERATIONS`. |
| `docs/security/THREAT_MODEL.md` | Documentation artifact describing `THREAT MODEL`. |
| `docs/site/services.md` | Documentation artifact describing `services`. |
| `docs/site/verify.md` | Documentation artifact describing `verify`. |
| `docs/structure/CANONICAL_CBOR_VECTORS_README.md` | Documentation artifact describing `CANONICAL CBOR VECTORS README`. |
| `docs/structure/DOC_CODE_SEPARATION_POLICY.md` | Documentation artifact describing `DOC CODE SEPARATION POLICY`. |
| `docs/structure/OPERATOR_STUB_VECTORS_README.txt` | Documentation artifact describing `OPERATOR STUB VECTORS README`. |
| `docs/structure/PROJECT_FILE_INVENTORY.md` | Documentation artifact describing `PROJECT FILE INVENTORY`. |
| `document_guidelines/EquationCode/BRIDGE.md` | Document-governance guideline artifact for `BRIDGE`. |
| `document_guidelines/EquationCode/ECOSYSTEM.md` | Document-governance guideline artifact for `ECOSYSTEM`. |
| `document_guidelines/EquationCode/EQC.md` | Document-governance guideline artifact for `EQC`. |
| `document_guidelines/EquationCode/LICENSE` | Document-governance guideline artifact for `LICENSE`. |
| `document_guidelines/EquationCode/README.md` | Document-governance guideline artifact for `README`. |
| `ecosystem-compatibility-aggregate.yaml` | Root-level project artifact `ecosystem-compatibility-aggregate.yaml` used by repository workflows. |
| `ecosystem-graph.yaml` | Relationship graph for ecosystem artifacts. |
| `ecosystem-registry.yaml` | Registry of ecosystem artifacts and metadata. |
| `ecosystem-validation-log.md` | Validation log for ecosystem governance updates. |
| `ecosystem.md` | Ecosystem index and governance/control mapping. |
| `ecosystem/tooling-manifest.yaml` | Ecosystem support artifact `tooling-manifest.yaml`. |
| `artifacts/inputs/fixtures/checkpoint-restore/checkpoint_input.json` | Input fixture artifact used for deterministic test scenarios (`checkpoint-restore`). |
| `artifacts/inputs/fixtures/checkpoint-restore/fixture-manifest.json` | Input fixture artifact used for deterministic test scenarios (`checkpoint-restore`). |
| `artifacts/inputs/fixtures/checkpoint-restore/restore_request.json` | Input fixture artifact used for deterministic test scenarios (`checkpoint-restore`). |
| `artifacts/inputs/fixtures/failure-injection/faulty_request.json` | Input fixture artifact used for deterministic test scenarios (`failure-injection`). |
| `artifacts/inputs/fixtures/failure-injection/fixture-manifest.json` | Input fixture artifact used for deterministic test scenarios (`failure-injection`). |
| `artifacts/inputs/fixtures/hello-core/checkpoint.json` | Input fixture artifact used for deterministic test scenarios (`hello-core`). |
| `artifacts/inputs/fixtures/hello-core/execution_certificate.json` | Input fixture artifact used for deterministic test scenarios (`hello-core`). |
| `artifacts/inputs/fixtures/hello-core/fixture-manifest.json` | Input fixture artifact used for deterministic test scenarios (`hello-core`). |
| `artifacts/inputs/fixtures/hello-core/manifest.core.yaml` | Input fixture artifact used for deterministic test scenarios (`hello-core`). |
| `artifacts/inputs/fixtures/hello-core/model_ir.json` | Input fixture artifact used for deterministic test scenarios (`hello-core`). |
| `artifacts/inputs/fixtures/hello-core/tiny_synth_dataset.jsonl` | Input fixture artifact used for deterministic test scenarios (`hello-core`). |
| `artifacts/inputs/fixtures/hello-core/trace.json` | Input fixture artifact used for deterministic test scenarios (`hello-core`). |
| `artifacts/inputs/fixtures/mini-tracking/inputs.json` | Input fixture artifact used for deterministic test scenarios (`mini-tracking`). |
| `artifacts/inputs/fixtures/perf-scale/batch.json` | Input fixture artifact used for deterministic test scenarios (`perf-scale`). |
| `artifacts/inputs/fixtures/perf-scale/fixture-manifest.json` | Input fixture artifact used for deterministic test scenarios (`perf-scale`). |
| `artifacts/inputs/fixtures/registry-lifecycle/fixture-manifest.json` | Input fixture artifact used for deterministic test scenarios (`registry-lifecycle`). |
| `artifacts/inputs/fixtures/registry-lifecycle/stage_transition.json` | Input fixture artifact used for deterministic test scenarios (`registry-lifecycle`). |
| `artifacts/inputs/fixtures/registry-lifecycle/version_create.json` | Input fixture artifact used for deterministic test scenarios (`registry-lifecycle`). |
| `artifacts/inputs/fixtures/replay-determinism/fixture-manifest.json` | Input fixture artifact used for deterministic test scenarios (`replay-determinism`). |
| `artifacts/inputs/fixtures/replay-determinism/trace.json` | Input fixture artifact used for deterministic test scenarios (`replay-determinism`). |
| `artifacts/inputs/fixtures/replay-suite-1/fixture-manifest.json` | Input fixture artifact used for deterministic test scenarios (`replay-suite-1`). |
| `artifacts/inputs/fixtures/replay-suite-1/trace.json` | Input fixture artifact used for deterministic test scenarios (`replay-suite-1`). |
| `artifacts/inputs/fixtures/tracking-monitoring/fixture-manifest.json` | Input fixture artifact used for deterministic test scenarios (`tracking-monitoring`). |
| `artifacts/inputs/fixtures/tracking-monitoring/run_event.json` | Input fixture artifact used for deterministic test scenarios (`tracking-monitoring`). |
| `artifacts/generated/bindings.py` | Code generation output artifact for `bindings`. |
| `artifacts/generated/clean_build/bindings.py` | Code generation output artifact for `bindings`. |
| `artifacts/generated/clean_build/error.py` | Code generation output artifact for `error`. |
| `artifacts/generated/clean_build/models.py` | Code generation output artifact for `models`. |
| `artifacts/generated/clean_build/operators.py` | Code generation output artifact for `operators`. |
| `artifacts/generated/clean_build/validators.py` | Code generation output artifact for `validators`. |
| `artifacts/generated/codegen_manifest.json` | Code generation output artifact for `codegen manifest`. |
| `artifacts/generated/deploy/confidential/bundle_manifest.json` | Code generation output artifact for `bundle manifest`. |
| `artifacts/generated/deploy/confidential/policy_bindings.json` | Code generation output artifact for `policy bindings`. |
| `artifacts/generated/deploy/confidential/runtime_config.json` | Code generation output artifact for `runtime config`. |
| `artifacts/generated/deploy/env_manifest.json` | Code generation output artifact for `env manifest`. |
| `artifacts/generated/deploy/managed/bundle_manifest.json` | Code generation output artifact for `bundle manifest`. |
| `artifacts/generated/deploy/managed/policy_bindings.json` | Code generation output artifact for `policy bindings`. |
| `artifacts/generated/deploy/managed/runtime_config.json` | Code generation output artifact for `runtime config`. |
| `artifacts/generated/deploy/migration_plan.json` | Code generation output artifact for `migration plan`. |
| `artifacts/generated/deploy/overlays/dev.json` | Code generation output artifact for `dev`. |
| `artifacts/generated/deploy/overlays/index.json` | Code generation output artifact for `index`. |
| `artifacts/generated/deploy/overlays/prod.json` | Code generation output artifact for `prod`. |
| `artifacts/generated/deploy/overlays/staging.json` | Code generation output artifact for `staging`. |
| `artifacts/generated/deploy/regulated/bundle_manifest.json` | Code generation output artifact for `bundle manifest`. |
| `artifacts/generated/deploy/regulated/policy_bindings.json` | Code generation output artifact for `policy bindings`. |
| `artifacts/generated/deploy/regulated/runtime_config.json` | Code generation output artifact for `runtime config`. |
| `artifacts/generated/error.py` | Code generation output artifact for `error`. |
| `artifacts/generated/input_hashes.json` | Code generation output artifact for `input hashes`. |
| `artifacts/generated/models.py` | Code generation output artifact for `models`. |
| `artifacts/generated/operators.py` | Code generation output artifact for `operators`. |
| `artifacts/generated/validators.py` | Code generation output artifact for `validators`. |
| `artifacts/expected/goldens/checkpoint-restore/checkpoint_expected.json` | Golden expected output artifact for `checkpoint-restore` comparisons. |
| `artifacts/expected/goldens/checkpoint-restore/golden-manifest.json` | Golden expected output artifact for `checkpoint-restore` comparisons. |
| `artifacts/expected/goldens/checkpoint-restore/restore_expected.json` | Golden expected output artifact for `checkpoint-restore` comparisons. |
| `artifacts/expected/goldens/failure-injection/faulty_expected.json` | Golden expected output artifact for `failure-injection` comparisons. |
| `artifacts/expected/goldens/failure-injection/golden-manifest.json` | Golden expected output artifact for `failure-injection` comparisons. |
| `artifacts/expected/goldens/golden_inventory.json` | Golden expected output artifact for `golden_inventory.json` comparisons. |
| `artifacts/expected/goldens/hello-core/checkpoint_header.json` | Golden expected output artifact for `hello-core` comparisons. |
| `artifacts/expected/goldens/hello-core/execution_certificate.json` | Golden expected output artifact for `hello-core` comparisons. |
| `artifacts/expected/goldens/hello-core/golden-identities.json` | Golden expected output artifact for `hello-core` comparisons. |
| `artifacts/expected/goldens/hello-core/golden-manifest.json` | Golden expected output artifact for `hello-core` comparisons. |
| `artifacts/expected/goldens/hello-core/trace_snippet.json` | Golden expected output artifact for `hello-core` comparisons. |
| `artifacts/expected/goldens/mini-tracking/expected.json` | Golden expected output artifact for `mini-tracking` comparisons. |
| `artifacts/expected/goldens/perf-scale/forward_expected.json` | Golden expected output artifact for `perf-scale` comparisons. |
| `artifacts/expected/goldens/perf-scale/golden-manifest.json` | Golden expected output artifact for `perf-scale` comparisons. |
| `artifacts/expected/goldens/registry-lifecycle/golden-manifest.json` | Golden expected output artifact for `registry-lifecycle` comparisons. |
| `artifacts/expected/goldens/registry-lifecycle/stage_transition_expected.json` | Golden expected output artifact for `registry-lifecycle` comparisons. |
| `artifacts/expected/goldens/registry-lifecycle/version_create_expected.json` | Golden expected output artifact for `registry-lifecycle` comparisons. |
| `artifacts/expected/goldens/replay-determinism/golden-manifest.json` | Golden expected output artifact for `replay-determinism` comparisons. |
| `artifacts/expected/goldens/replay-determinism/replay_expected.json` | Golden expected output artifact for `replay-determinism` comparisons. |
| `artifacts/expected/goldens/replay-suite-1/golden-manifest.json` | Golden expected output artifact for `replay-suite-1` comparisons. |
| `artifacts/expected/goldens/replay-suite-1/trace_expected.json` | Golden expected output artifact for `replay-suite-1` comparisons. |
| `artifacts/expected/goldens/tracking-monitoring/golden-manifest.json` | Golden expected output artifact for `tracking-monitoring` comparisons. |
| `artifacts/expected/goldens/tracking-monitoring/metric_log_expected.json` | Golden expected output artifact for `tracking-monitoring` comparisons. |
| `migration-plan-template.yaml` | Root-level project artifact `migration-plan-template.yaml` used by repository workflows. |
| `milestones.txt` | Milestone roadmap, completion evidence, and delivery status. |
| `portfolio-release-notes-template.md` | Template for portfolio-level release notes. |
| `pyproject.toml` | Python project metadata and test/tool configuration. |
| `evidence/coverage/operator_coverage.json` | Generated evidence/report artifact for `coverage`. |
| `evidence/deploy/drift.json` | Generated evidence/report artifact for `deploy`. |
| `evidence/deploy/latest.json` | Generated evidence/report artifact for `deploy`. |
| `evidence/deploy/parity.json` | Generated evidence/report artifact for `deploy`. |
| `evidence/deploy/rollback.json` | Generated evidence/report artifact for `deploy`. |
| `evidence/deploy/state/staging_active.json` | Generated evidence/report artifact for `deploy`. |
| `evidence/deploy/state/staging_previous.json` | Generated evidence/report artifact for `deploy`. |
| `evidence/ga/latest.json` | Generated evidence/report artifact for `ga`. |
| `evidence/ga/release_candidate_verification.json` | Generated evidence/report artifact for `ga`. |
| `evidence/observability/alert_test.json` | Generated evidence/report artifact for `observability`. |
| `evidence/observability/dashboard_inventory.json` | Generated evidence/report artifact for `observability`. |
| `evidence/observability/incident_drill.json` | Generated evidence/report artifact for `observability`. |
| `evidence/observability/latest.json` | Generated evidence/report artifact for `observability`. |
| `evidence/observability/lineage_index.json` | Generated evidence/report artifact for `observability`. |
| `evidence/observability/slo_status.json` | Generated evidence/report artifact for `observability`. |
| `evidence/observability/synthetic_probe.json` | Generated evidence/report artifact for `observability`. |
| `evidence/recovery/backup-restore-drill.json` | Generated evidence/report artifact for `recovery`. |
| `evidence/recovery/checkpoint-backup.json` | Generated evidence/report artifact for `recovery`. |
| `evidence/recovery/latest.json` | Generated evidence/report artifact for `recovery`. |
| `evidence/recovery/replay-proof.txt` | Generated evidence/report artifact for `recovery`. |
| `evidence/repro/compare-20260228.md` | Generated evidence/report artifact for `repro`. |
| `evidence/repro/compare-template.md` | Generated evidence/report artifact for `repro`. |
| `evidence/repro/dependency-lock.sha256` | Generated evidence/report artifact for `repro`. |
| `evidence/repro/hashes.txt` | Generated evidence/report artifact for `repro`. |
| `evidence/repro/run-checklist.md` | Generated evidence/report artifact for `repro`. |
| `evidence/security/audit.log.jsonl` | Generated evidence/report artifact for `security`. |
| `evidence/security/build_provenance.json` | Generated evidence/report artifact for `security`. |
| `evidence/security/latest.json` | Generated evidence/report artifact for `security`. |
| `evidence/security/sbom.json` | Generated evidence/report artifact for `security`. |
| `evidence/structure/latest.json` | Generated evidence/report artifact for `structure`. |
| `evidence/validation/external_security_review.md` | Generated evidence/report artifact for `validation`. |
| `evidence/validation/independent_verification_summary.json` | Generated evidence/report artifact for `validation`. |
| `evidence/validation/issues.json` | Generated evidence/report artifact for `validation`. |
| `evidence/validation/latest.json` | Generated evidence/report artifact for `validation`. |
| `evidence/validation/runs/run-01-linux-mint.json` | Generated evidence/report artifact for `validation`. |
| `evidence/validation/runs/run-02-ubuntu-wsl.json` | Generated evidence/report artifact for `validation`. |
| `evidence/validation/runs/run-03-docs-only-cleanroom.json` | Generated evidence/report artifact for `validation`. |
| `evidence/validation/scorecards/run-01-linux-mint.json` | Generated evidence/report artifact for `validation`. |
| `evidence/validation/scorecards/run-02-ubuntu-wsl.json` | Generated evidence/report artifact for `validation`. |
| `evidence/validation/scorecards/run-03-docs-only-cleanroom.json` | Generated evidence/report artifact for `validation`. |
| `evidence/validation/transcripts/run-01-linux-mint.md` | Generated evidence/report artifact for `validation`. |
| `evidence/validation/transcripts/run-02-ubuntu-wsl.md` | Generated evidence/report artifact for `validation`. |
| `evidence/validation/transcripts/run-03-docs-only-cleanroom.md` | Generated evidence/report artifact for `validation`. |
| `requirements.lock` | Pinned dependency lock file for reproducible environments. |
| `schemas/SCHEMA_CONVENTIONS.txt` | Schema/meta-schema artifact for `SCHEMA CONVENTIONS` validation. |
| `schemas/SCHEMA_FORMAT_DECISION.txt` | Schema/meta-schema artifact for `SCHEMA FORMAT DECISION` validation. |
| `schemas/contract_schema_meta.json` | Schema/meta-schema artifact for `contract schema meta` validation. |
| `schemas/l3_operator_error_vectors.schema.json` | Schema/meta-schema artifact for `l3 operator error vectors.schema` validation. |
| `schemas/l3_operator_vectors.schema.json` | Schema/meta-schema artifact for `l3 operator vectors.schema` validation. |
| `schemas/pilot/l1_api_interfaces.schema.json` | Schema/meta-schema artifact for `l1 api interfaces.schema` validation. |
| `schemas/pilot/l1_canonical_cbor_profile.schema.json` | Schema/meta-schema artifact for `l1 canonical cbor profile.schema` validation. |
| `schemas/pilot/l1_data_structures.schema.json` | Schema/meta-schema artifact for `l1 data structures.schema` validation. |
| `schemas/pilot/l1_dependency_lock_policy.schema.json` | Schema/meta-schema artifact for `l1 dependency lock policy.schema` validation. |
| `schemas/pilot/l1_determinism_profiles.schema.json` | Schema/meta-schema artifact for `l1 determinism profiles.schema` validation. |
| `schemas/pilot/l1_digest_catalog.schema.json` | Schema/meta-schema artifact for `l1 digest catalog.schema` validation. |
| `schemas/pilot/l1_environment_manifest.schema.json` | Schema/meta-schema artifact for `l1 environment manifest.schema` validation. |
| `schemas/pilot/l1_error_codes.schema.json` | Schema/meta-schema artifact for `l1 error codes.schema` validation. |
| `schemas/pilot/l1_normativity_legend.schema.json` | Schema/meta-schema artifact for `l1 normativity legend.schema` validation. |
| `schemas/pilot/l1_operator_registry_schema.schema.json` | Schema/meta-schema artifact for `l1 operator registry schema.schema` validation. |
| `schemas/pilot/l1_redaction_policy.schema.json` | Schema/meta-schema artifact for `l1 redaction policy.schema` validation. |
| `schemas/pilot/l2_authz-capability-matrix.schema.json` | Schema/meta-schema artifact for `l2 authz capability matrix.schema` validation. |
| `schemas/pilot/l2_checkpoint-schema.schema.json` | Schema/meta-schema artifact for `l2 checkpoint schema.schema` validation. |
| `schemas/pilot/l2_config-schema.schema.json` | Schema/meta-schema artifact for `l2 config schema.schema` validation. |
| `schemas/pilot/l2_config_schema.schema.json` | Schema/meta-schema artifact for `l2 config schema.schema` validation. |
| `schemas/pilot/l2_data-lineage.schema.json` | Schema/meta-schema artifact for `l2 data lineage.schema` validation. |
| `schemas/pilot/l2_data-nextbatch.schema.json` | Schema/meta-schema artifact for `l2 data nextbatch.schema` validation. |
| `schemas/pilot/l2_deployment-runbook.schema.json` | Schema/meta-schema artifact for `l2 deployment runbook.schema` validation. |
| `schemas/pilot/l2_differentialprivacy-apply.schema.json` | Schema/meta-schema artifact for `l2 differentialprivacy apply.schema` validation. |
| `schemas/pilot/l2_evaluation-harness.schema.json` | Schema/meta-schema artifact for `l2 evaluation harness.schema` validation. |
| `schemas/pilot/l2_execution-certificate.schema.json` | Schema/meta-schema artifact for `l2 execution certificate.schema` validation. |
| `schemas/pilot/l2_experiment-tracking.schema.json` | Schema/meta-schema artifact for `l2 experiment tracking.schema` validation. |
| `schemas/pilot/l2_glyphser-kernel-v3.22-os.schema.json` | Schema/meta-schema artifact for `l2 glyphser kernel v3.22 os.schema` validation. |
| `schemas/pilot/l2_model-registry.schema.json` | Schema/meta-schema artifact for `l2 model registry.schema` validation. |
| `schemas/pilot/l2_modelir-executor.schema.json` | Schema/meta-schema artifact for `l2 modelir executor.schema` validation. |
| `schemas/pilot/l2_monitoring-policy.schema.json` | Schema/meta-schema artifact for `l2 monitoring policy.schema` validation. |
| `schemas/pilot/l2_pipeline-orchestrator.schema.json` | Schema/meta-schema artifact for `l2 pipeline orchestrator.schema` validation. |
| `schemas/pilot/l2_replay-determinism.schema.json` | Schema/meta-schema artifact for `l2 replay determinism.schema` validation. |
| `schemas/pilot/l2_run-commit-wal.schema.json` | Schema/meta-schema artifact for `l2 run commit wal.schema` validation. |
| `schemas/pilot/l2_security-compliance-profile.schema.json` | Schema/meta-schema artifact for `l2 security compliance profile.schema` validation. |
| `schemas/pilot/l2_tmmu-allocation.schema.json` | Schema/meta-schema artifact for `l2 tmmu allocation.schema` validation. |
| `schemas/pilot/l2_trace-sidecar.schema.json` | Schema/meta-schema artifact for `l2 trace sidecar.schema` validation. |
| `schemas/pilot/l3_compatibility-test-matrix.schema.json` | Schema/meta-schema artifact for `l3 compatibility test matrix.schema` validation. |
| `schemas/pilot/l3_conformance-ci-pipeline.schema.json` | Schema/meta-schema artifact for `l3 conformance ci pipeline.schema` validation. |
| `schemas/pilot/l3_conformance-harness-guide.schema.json` | Schema/meta-schema artifact for `l3 conformance harness guide.schema` validation. |
| `schemas/pilot/l3_coverage-targets.schema.json` | Schema/meta-schema artifact for `l3 coverage targets.schema` validation. |
| `schemas/pilot/l3_data-contract-fuzzing-guide.schema.json` | Schema/meta-schema artifact for `l3 data contract fuzzing guide.schema` validation. |
| `schemas/pilot/l3_failure-injection-index.schema.json` | Schema/meta-schema artifact for `l3 failure injection index.schema` validation. |
| `schemas/pilot/l3_failure-injection-scenarios.schema.json` | Schema/meta-schema artifact for `l3 failure injection scenarios.schema` validation. |
| `schemas/pilot/l3_game-day-scenarios.schema.json` | Schema/meta-schema artifact for `l3 game day scenarios.schema` validation. |
| `schemas/pilot/l3_integration-test-matrix.schema.json` | Schema/meta-schema artifact for `l3 integration test matrix.schema` validation. |
| `schemas/pilot/l3_performance-plan.schema.json` | Schema/meta-schema artifact for `l3 performance plan.schema` validation. |
| `schemas/pilot/l3_release-gates.schema.json` | Schema/meta-schema artifact for `l3 release gates.schema` validation. |
| `schemas/pilot/l3_storage-recovery-test-matrix.schema.json` | Schema/meta-schema artifact for `l3 storage recovery test matrix.schema` validation. |
| `schemas/pilot/l3_test-plan.schema.json` | Schema/meta-schema artifact for `l3 test plan.schema` validation. |
| `schemas/pilot/l3_test-vectors-catalog.schema.json` | Schema/meta-schema artifact for `l3 test vectors catalog.schema` validation. |
| `schemas/pilot/l3_test_plan.schema.json` | Schema/meta-schema artifact for `l3 test plan.schema` validation. |
| `schemas/pilot/l4_api-lifecycle-and-deprecation-policy.schema.json` | Schema/meta-schema artifact for `l4 api lifecycle and deprecation policy.schema` validation. |
| `schemas/pilot/l4_architecture-decisions-log.schema.json` | Schema/meta-schema artifact for `l4 architecture decisions log.schema` validation. |
| `schemas/pilot/l4_artifact-store-adapter-guide.schema.json` | Schema/meta-schema artifact for `l4 artifact store adapter guide.schema` validation. |
| `schemas/pilot/l4_backend-adapter-guide.schema.json` | Schema/meta-schema artifact for `l4 backend adapter guide.schema` validation. |
| `schemas/pilot/l4_backend-feature-matrix.schema.json` | Schema/meta-schema artifact for `l4 backend feature matrix.schema` validation. |
| `schemas/pilot/l4_benchmark-evidence-spec.schema.json` | Schema/meta-schema artifact for `l4 benchmark evidence spec.schema` validation. |
| `schemas/pilot/l4_brownfield-deployment-guide.schema.json` | Schema/meta-schema artifact for `l4 brownfield deployment guide.schema` validation. |
| `schemas/pilot/l4_build-and-ci-matrix.schema.json` | Schema/meta-schema artifact for `l4 build and ci matrix.schema` validation. |
| `schemas/pilot/l4_canonical-hashing-reference.schema.json` | Schema/meta-schema artifact for `l4 canonical hashing reference.schema` validation. |
| `schemas/pilot/l4_change-control-playbook.schema.json` | Schema/meta-schema artifact for `l4 change control playbook.schema` validation. |
| `schemas/pilot/l4_cli-command-profiles.schema.json` | Schema/meta-schema artifact for `l4 cli command profiles.schema` validation. |
| `schemas/pilot/l4_code-generation-mapping.schema.json` | Schema/meta-schema artifact for `l4 code generation mapping.schema` validation. |
| `schemas/pilot/l4_coding-standards.schema.json` | Schema/meta-schema artifact for `l4 coding standards.schema` validation. |
| `schemas/pilot/l4_command-reference.schema.json` | Schema/meta-schema artifact for `l4 command reference.schema` validation. |
| `schemas/pilot/l4_common-pitfalls-guide.schema.json` | Schema/meta-schema artifact for `l4 common pitfalls guide.schema` validation. |
| `schemas/pilot/l4_community-governance-model.schema.json` | Schema/meta-schema artifact for `l4 community governance model.schema` validation. |
| `schemas/pilot/l4_contracts-artifact-lifecycle.schema.json` | Schema/meta-schema artifact for `l4 contracts artifact lifecycle.schema` validation. |
| `schemas/pilot/l4_contributing-workflow.schema.json` | Schema/meta-schema artifact for `l4 contributing workflow.schema` validation. |
| `schemas/pilot/l4_debugging-playbook.schema.json` | Schema/meta-schema artifact for `l4 debugging playbook.schema` validation. |
| `schemas/pilot/l4_determinism-audit-playbook.schema.json` | Schema/meta-schema artifact for `l4 determinism audit playbook.schema` validation. |
| `schemas/pilot/l4_determinism-debug-checklist.schema.json` | Schema/meta-schema artifact for `l4 determinism debug checklist.schema` validation. |
| `schemas/pilot/l4_deterministic-rng-implementation-guide.schema.json` | Schema/meta-schema artifact for `l4 deterministic rng implementation guide.schema` validation. |
| `schemas/pilot/l4_developer-setup.schema.json` | Schema/meta-schema artifact for `l4 developer setup.schema` validation. |
| `schemas/pilot/l4_developer-troubleshooting-faq.schema.json` | Schema/meta-schema artifact for `l4 developer troubleshooting faq.schema` validation. |
| `schemas/pilot/l4_disaster-recovery-operations-runbook.schema.json` | Schema/meta-schema artifact for `l4 disaster recovery operations runbook.schema` validation. |
| `schemas/pilot/l4_distributed-failure-recovery-guide.schema.json` | Schema/meta-schema artifact for `l4 distributed failure recovery guide.schema` validation. |
| `schemas/pilot/l4_ecosystem-expansion-roadmap.schema.json` | Schema/meta-schema artifact for `l4 ecosystem expansion roadmap.schema` validation. |
| `schemas/pilot/l4_eqc-ci-policy.schema.json` | Schema/meta-schema artifact for `l4 eqc ci policy.schema` validation. |
| `schemas/pilot/l4_evidence-catalog.schema.json` | Schema/meta-schema artifact for `l4 evidence catalog.schema` validation. |
| `schemas/pilot/l4_expansion-catalog-041-250.schema.json` | Schema/meta-schema artifact for `l4 expansion catalog 041 250.schema` validation. |
| `schemas/pilot/l4_external-interface-standard.schema.json` | Schema/meta-schema artifact for `l4 external interface standard.schema` validation. |
| `schemas/pilot/l4_fixtures-and-golden-data.schema.json` | Schema/meta-schema artifact for `l4 fixtures and golden data.schema` validation. |
| `schemas/pilot/l4_formal-verification-roadmap.schema.json` | Schema/meta-schema artifact for `l4 formal verification roadmap.schema` validation. |
| `schemas/pilot/l4_gentle-introduction.schema.json` | Schema/meta-schema artifact for `l4 gentle introduction.schema` validation. |
| `schemas/pilot/l4_hello-world-end-to-end-example.schema.json` | Schema/meta-schema artifact for `l4 hello world end to end example.schema` validation. |
| `schemas/pilot/l4_implementation-backlog.schema.json` | Schema/meta-schema artifact for `l4 implementation backlog.schema` validation. |
| `schemas/pilot/l4_implementation-roadmap.schema.json` | Schema/meta-schema artifact for `l4 implementation roadmap.schema` validation. |
| `schemas/pilot/l4_incident-postmortem-template.schema.json` | Schema/meta-schema artifact for `l4 incident postmortem template.schema` validation. |
| `schemas/pilot/l4_industry-productization-upgrade-plan.schema.json` | Schema/meta-schema artifact for `l4 industry productization upgrade plan.schema` validation. |
| `schemas/pilot/l4_interoperability-standards-bridge.schema.json` | Schema/meta-schema artifact for `l4 interoperability standards bridge.schema` validation. |
| `schemas/pilot/l4_local-replay-runbook.schema.json` | Schema/meta-schema artifact for `l4 local replay runbook.schema` validation. |
| `schemas/pilot/l4_migration-execution-guide.schema.json` | Schema/meta-schema artifact for `l4 migration execution guide.schema` validation. |
| `schemas/pilot/l4_module-scaffolding-guide.schema.json` | Schema/meta-schema artifact for `l4 module scaffolding guide.schema` validation. |
| `schemas/pilot/l4_operator-conformance-matrix.schema.json` | Schema/meta-schema artifact for `l4 operator conformance matrix.schema` validation. |
| `schemas/pilot/l4_operator-registry-cbor-contract.schema.json` | Schema/meta-schema artifact for `l4 operator registry cbor contract.schema` validation. |
| `schemas/pilot/l4_operator-sdk-scaffold-template.schema.json` | Schema/meta-schema artifact for `l4 operator sdk scaffold template.schema` validation. |
| `schemas/pilot/l4_pr-review-checklist.schema.json` | Schema/meta-schema artifact for `l4 pr review checklist.schema` validation. |
| `schemas/pilot/l4_profiling-and-optimization-guide.schema.json` | Schema/meta-schema artifact for `l4 profiling and optimization guide.schema` validation. |
| `schemas/pilot/l4_reference-implementations.schema.json` | Schema/meta-schema artifact for `l4 reference implementations.schema` validation. |
| `schemas/pilot/l4_reference-stack-minimal.schema.json` | Schema/meta-schema artifact for `l4 reference stack minimal.schema` validation. |
| `schemas/pilot/l4_release-evidence-assembler.schema.json` | Schema/meta-schema artifact for `l4 release evidence assembler.schema` validation. |
| `schemas/pilot/l4_repo-layout-and-interfaces.schema.json` | Schema/meta-schema artifact for `l4 repo layout and interfaces.schema` validation. |
| `schemas/pilot/l4_research-extensions-roadmap.schema.json` | Schema/meta-schema artifact for `l4 research extensions roadmap.schema` validation. |
| `schemas/pilot/l4_runtime-state-machine-reference.schema.json` | Schema/meta-schema artifact for `l4 runtime state machine reference.schema` validation. |
| `schemas/pilot/l4_schema-evolution-playbook.schema.json` | Schema/meta-schema artifact for `l4 schema evolution playbook.schema` validation. |
| `schemas/pilot/l4_scope-and-non-goals.schema.json` | Schema/meta-schema artifact for `l4 scope and non goals.schema` validation. |
| `schemas/pilot/l4_sdk-usage-guide.schema.json` | Schema/meta-schema artifact for `l4 sdk usage guide.schema` validation. |
| `schemas/pilot/l4_security-case-template.schema.json` | Schema/meta-schema artifact for `l4 security case template.schema` validation. |
| `schemas/pilot/l4_security-coding-checklist.schema.json` | Schema/meta-schema artifact for `l4 security coding checklist.schema` validation. |
| `schemas/pilot/l4_spec-lint-implementation.schema.json` | Schema/meta-schema artifact for `l4 spec lint implementation.schema` validation. |
| `schemas/pilot/l4_spec-lint-rules.schema.json` | Schema/meta-schema artifact for `l4 spec lint rules.schema` validation. |
| `schemas/pilot/l4_sre-incident-triage-playbook.schema.json` | Schema/meta-schema artifact for `l4 sre incident triage playbook.schema` validation. |
| `schemas/pilot/l4_test-harness-implementation.schema.json` | Schema/meta-schema artifact for `l4 test harness implementation.schema` validation. |
| `schemas/pilot/l4_third-party-operator-certification-program.schema.json` | Schema/meta-schema artifact for `l4 third party operator certification program.schema` validation. |
| `schemas/pilot/l4_threat-model-and-control-crosswalk.schema.json` | Schema/meta-schema artifact for `l4 threat model and control crosswalk.schema` validation. |
| `schemas/pilot/l4_tooling-and-automation-suite.schema.json` | Schema/meta-schema artifact for `l4 tooling and automation suite.schema` validation. |
| `schemas/pilot/l4_tooling-suite.schema.json` | Schema/meta-schema artifact for `l4 tooling suite.schema` validation. |
| `scripts/repro/host_meta.py` | Project artifact `host_meta.py` used by repository workflows. |
| `scripts/run_hello_core.py` | Project artifact `run_hello_core.py` used by repository workflows. |
| `semantic_lint_high_confidence.txt` | High-confidence semantic lint findings. |
| `semantic_lint_report.txt` | Full semantic lint report output. |
| `src/glyphser/api/runtime_api.py` | Runtime/source implementation module for `runtime api`. |
| `src/glyphser/api/validate_signature.py` | Runtime/source implementation module for `validate signature`. |
| `src/glyphser/backend/load_driver.py` | Runtime/source implementation module for `load driver`. |
| `src/glyphser/backend/reference_driver.py` | Runtime/source implementation module for `reference driver`. |
| `src/glyphser/cert/evidence_validate.py` | Runtime/source implementation module for `evidence validate`. |
| `src/glyphser/certificate/build.py` | Runtime/source implementation module for `build`. |
| `src/glyphser/checkpoint/migrate_checkpoint.py` | Runtime/source implementation module for `migrate checkpoint`. |
| `src/glyphser/checkpoint/restore.py` | Runtime/source implementation module for `restore`. |
| `src/glyphser/checkpoint/write.py` | Runtime/source implementation module for `write`. |
| `src/glyphser/config/migrate_manifest.py` | Runtime/source implementation module for `migrate manifest`. |
| `src/glyphser/contract/validate.py` | Runtime/source implementation module for `validate`. |
| `src/glyphser/data/next_batch.py` | Runtime/source implementation module for `next batch`. |
| `src/glyphser/data_structures/validate_struct.py` | Runtime/source implementation module for `validate struct`. |
| `src/glyphser/dp/apply.py` | Runtime/source implementation module for `apply`. |
| `src/glyphser/error/emit.py` | Runtime/source implementation module for `emit`. |
| `src/glyphser/fingerprint/state_fingerprint.py` | Runtime/source implementation module for `state fingerprint`. |
| `src/glyphser/legacy_import/legacy_framework.py` | Runtime/source implementation module for `legacy framework`. |
| `src/glyphser/model/build_grad_dependency_order.py` | Runtime/source implementation module for `build grad dependency order`. |
| `src/glyphser/model/collect_gradients.py` | Runtime/source implementation module for `collect gradients`. |
| `src/glyphser/model/dispatch_primitive.py` | Runtime/source implementation module for `dispatch primitive`. |
| `src/glyphser/model/forward.py` | Runtime/source implementation module for `forward`. |
| `src/glyphser/model/ir_schema.py` | Runtime/source implementation module for `ir schema`. |
| `src/glyphser/model/model_ir_executor.py` | Runtime/source implementation module for `model ir executor`. |
| `src/glyphser/model/topo_sort_nodes.py` | Runtime/source implementation module for `topo sort nodes`. |
| `src/glyphser/monitor/drift_compute.py` | Runtime/source implementation module for `drift compute`. |
| `src/glyphser/monitor/emit.py` | Runtime/source implementation module for `emit`. |
| `src/glyphser/monitor/register.py` | Runtime/source implementation module for `register`. |
| `src/glyphser/registry/interface_hash.py` | Runtime/source implementation module for `interface hash`. |
| `src/glyphser/registry/registry_builder.py` | Runtime/source implementation module for `registry builder`. |
| `src/glyphser/registry/stage_transition.py` | Runtime/source implementation module for `stage transition`. |
| `src/glyphser/registry/version_create.py` | Runtime/source implementation module for `version create`. |
| `src/glyphser/security/__init__.py` | Runtime/source implementation module for `init`. |
| `src/glyphser/security/audit.py` | Runtime/source implementation module for `audit`. |
| `src/glyphser/security/authz.py` | Runtime/source implementation module for `authz`. |
| `src/glyphser/serialization/canonical_cbor.py` | Runtime/source implementation module for `canonical cbor`. |
| `src/glyphser/storage/__init__.py` | Runtime/source implementation module for `init`. |
| `src/glyphser/storage/state_store.py` | Runtime/source implementation module for `state store`. |
| `src/glyphser/tmmu/commit_execution.py` | Runtime/source implementation module for `commit execution`. |
| `src/glyphser/tmmu/prepare_memory.py` | Runtime/source implementation module for `prepare memory`. |
| `src/glyphser/trace/compute_trace_hash.py` | Runtime/source implementation module for `compute trace hash`. |
| `src/glyphser/trace/migrate_trace.py` | Runtime/source implementation module for `migrate trace`. |
| `src/glyphser/trace/trace_sidecar.py` | Runtime/source implementation module for `trace sidecar`. |
| `src/glyphser/tracking/artifact_get.py` | Runtime/source implementation module for `artifact get`. |
| `src/glyphser/tracking/artifact_list.py` | Runtime/source implementation module for `artifact list`. |
| `src/glyphser/tracking/artifact_put.py` | Runtime/source implementation module for `artifact put`. |
| `src/glyphser/tracking/artifact_tombstone.py` | Runtime/source implementation module for `artifact tombstone`. |
| `src/glyphser/tracking/metric_log.py` | Runtime/source implementation module for `metric log`. |
| `src/glyphser/tracking/run_create.py` | Runtime/source implementation module for `run create`. |
| `src/glyphser/tracking/run_end.py` | Runtime/source implementation module for `run end`. |
| `src/glyphser/tracking/run_start.py` | Runtime/source implementation module for `run start`. |
| `temp/RESUME CODEX` | Temporary working artifact for `RESUME CODEX`. |
| `temp/checkpoint-restore/ckpt-1.json` | Temporary working artifact for `checkpoint-restore`. |
| `tests/__init__.py` | Automated test artifact validating `init` behavior. |
| `tests/api/__init__.py` | Automated test artifact validating `init` behavior. |
| `tests/api/test_api_cli.py` | Automated test artifact validating `test api cli` behavior. |
| `tests/api/test_api_contract_gate.py` | Automated test artifact validating `test api contract gate` behavior. |
| `tests/api/test_runtime_api.py` | Automated test artifact validating `test runtime api` behavior. |
| `tests/api/test_validate_signature.py` | Automated test artifact validating `test validate signature` behavior. |
| `tests/canonical_cbor/__init__.py` | Automated test artifact validating `init` behavior. |
| `tests/canonical_cbor/test_fuzz.py` | Automated test artifact validating `test fuzz` behavior. |
| `tests/canonical_cbor/test_vectors.py` | Automated test artifact validating `test vectors` behavior. |
| `tests/canonical_cbor/vector_loader.py` | Automated test artifact validating `vector loader` behavior. |
| `tests/chaos/test_distributed_chaos.py` | Automated test artifact validating `test distributed chaos` behavior. |
| `tests/conformance/artifacts/inputs/vectors/interface_hash/vectors.json` | Automated test artifact validating `vectors` behavior. |
| `tests/conformance/artifacts/inputs/vectors/operators/Glyphser_Backend_LoadDriver.json` | Automated test artifact validating `Glyphser Backend LoadDriver` behavior. |
| `tests/conformance/artifacts/inputs/vectors/operators/Glyphser_Certificate_EvidenceValidate.json` | Automated test artifact validating `Glyphser Certificate EvidenceValidate` behavior. |
| `tests/conformance/artifacts/inputs/vectors/operators/Glyphser_Checkpoint_CheckpointMigrate.json` | Automated test artifact validating `Glyphser Checkpoint CheckpointMigrate` behavior. |
| `tests/conformance/artifacts/inputs/vectors/operators/Glyphser_Checkpoint_Restore.json` | Automated test artifact validating `Glyphser Checkpoint Restore` behavior. |
| `tests/conformance/artifacts/inputs/vectors/operators/Glyphser_Config_ManifestMigrate.json` | Automated test artifact validating `Glyphser Config ManifestMigrate` behavior. |
| `tests/conformance/artifacts/inputs/vectors/operators/Glyphser_Data_NextBatch.json` | Automated test artifact validating `Glyphser Data NextBatch` behavior. |
| `tests/conformance/artifacts/inputs/vectors/operators/Glyphser_DifferentialPrivacy_Apply.json` | Automated test artifact validating `Glyphser DifferentialPrivacy Apply` behavior. |
| `tests/conformance/artifacts/inputs/vectors/operators/Glyphser_Error_Emit.json` | Automated test artifact validating `Glyphser Error Emit` behavior. |
| `tests/conformance/artifacts/inputs/vectors/operators/Glyphser_IO_SaveCheckpoint.json` | Automated test artifact validating `Glyphser IO SaveCheckpoint` behavior. |
| `tests/conformance/artifacts/inputs/vectors/operators/Glyphser_Import_LegacyFramework.json` | Automated test artifact validating `Glyphser Import LegacyFramework` behavior. |
| `tests/conformance/artifacts/inputs/vectors/operators/Glyphser_Model_Forward.json` | Automated test artifact validating `Glyphser Model Forward` behavior. |
| `tests/conformance/artifacts/inputs/vectors/operators/Glyphser_Model_ModelIR_Executor.json` | Automated test artifact validating `Glyphser Model ModelIR Executor` behavior. |
| `tests/conformance/artifacts/inputs/vectors/operators/Glyphser_Monitor_DriftCompute.json` | Automated test artifact validating `Glyphser Monitor DriftCompute` behavior. |
| `tests/conformance/artifacts/inputs/vectors/operators/Glyphser_Monitor_Emit.json` | Automated test artifact validating `Glyphser Monitor Emit` behavior. |
| `tests/conformance/artifacts/inputs/vectors/operators/Glyphser_Monitor_Register.json` | Automated test artifact validating `Glyphser Monitor Register` behavior. |
| `tests/conformance/artifacts/inputs/vectors/operators/Glyphser_Registry_StageTransition.json` | Automated test artifact validating `Glyphser Registry StageTransition` behavior. |
| `tests/conformance/artifacts/inputs/vectors/operators/Glyphser_Registry_VersionCreate.json` | Automated test artifact validating `Glyphser Registry VersionCreate` behavior. |
| `tests/conformance/artifacts/inputs/vectors/operators/Glyphser_TMMU_PrepareMemory.json` | Automated test artifact validating `Glyphser TMMU PrepareMemory` behavior. |
| `tests/conformance/artifacts/inputs/vectors/operators/Glyphser_Trace_TraceMigrate.json` | Automated test artifact validating `Glyphser Trace TraceMigrate` behavior. |
| `tests/conformance/artifacts/inputs/vectors/operators/Glyphser_Tracking_ArtifactGet.json` | Automated test artifact validating `Glyphser Tracking ArtifactGet` behavior. |
| `tests/conformance/artifacts/inputs/vectors/operators/Glyphser_Tracking_ArtifactList.json` | Automated test artifact validating `Glyphser Tracking ArtifactList` behavior. |
| `tests/conformance/artifacts/inputs/vectors/operators/Glyphser_Tracking_ArtifactPut.json` | Automated test artifact validating `Glyphser Tracking ArtifactPut` behavior. |
| `tests/conformance/artifacts/inputs/vectors/operators/Glyphser_Tracking_ArtifactTombstone.json` | Automated test artifact validating `Glyphser Tracking ArtifactTombstone` behavior. |
| `tests/conformance/artifacts/inputs/vectors/operators/Glyphser_Tracking_MetricLog.json` | Automated test artifact validating `Glyphser Tracking MetricLog` behavior. |
| `tests/conformance/artifacts/inputs/vectors/operators/Glyphser_Tracking_RunCreate.json` | Automated test artifact validating `Glyphser Tracking RunCreate` behavior. |
| `tests/conformance/artifacts/inputs/vectors/operators/Glyphser_Tracking_RunEnd.json` | Automated test artifact validating `Glyphser Tracking RunEnd` behavior. |
| `tests/conformance/artifacts/inputs/vectors/operators/Glyphser_Tracking_RunStart.json` | Automated test artifact validating `Glyphser Tracking RunStart` behavior. |
| `tests/conformance/artifacts/inputs/vectors/storage/state_recovery_vectors.json` | Automated test artifact validating `state recovery vectors` behavior. |
| `tests/conftest.py` | Automated test artifact validating `conftest` behavior. |
| `tests/data_structures/__init__.py` | Automated test artifact validating `init` behavior. |
| `tests/data_structures/test_validate_struct.py` | Automated test artifact validating `test validate struct` behavior. |
| `tests/data_structures/test_vectors.py` | Automated test artifact validating `test vectors` behavior. |
| `tests/deploy/test_deploy_pipeline_gate.py` | Automated test artifact validating `test deploy pipeline gate` behavior. |
| `tests/artifacts/inputs/fixtures/test_mini_tracking_fixture.py` | Automated test artifact validating `test mini tracking fixture` behavior. |
| `tests/fuzz/test_checkpoint_decode_fuzz.py` | Automated test artifact validating `test checkpoint decode fuzz` behavior. |
| `tests/fuzz/test_ir_validation_fuzz.py` | Automated test artifact validating `test ir validation fuzz` behavior. |
| `tests/fuzz/test_manifest_parser_fuzz.py` | Automated test artifact validating `test manifest parser fuzz` behavior. |
| `tests/fuzz/test_schema_parsing_fuzz.py` | Automated test artifact validating `test schema parsing fuzz` behavior. |
| `tests/fuzz/test_tmmu_planner_invariants.py` | Automated test artifact validating `test tmmu planner invariants` behavior. |
| `tests/fuzz/test_trace_parser_fuzz.py` | Automated test artifact validating `test trace parser fuzz` behavior. |
| `tests/ga/test_ga_release_gate.py` | Automated test artifact validating `test ga release gate` behavior. |
| `tests/artifacts/expected/goldens/test_golden_inventory.py` | Automated test artifact validating `test golden inventory` behavior. |
| `tests/interface_hash/__init__.py` | Automated test artifact validating `init` behavior. |
| `tests/interface_hash/test_vectors.py` | Automated test artifact validating `test vectors` behavior. |
| `tests/operators/__init__.py` | Automated test artifact validating `init` behavior. |
| `tests/operators/test_glyphser_backend_stubs.py` | Automated test artifact validating `test glyphser backend stubs` behavior. |
| `tests/operators/test_glyphser_certificate_stubs.py` | Automated test artifact validating `test glyphser certificate stubs` behavior. |
| `tests/operators/test_glyphser_checkpoint_stubs.py` | Automated test artifact validating `test glyphser checkpoint stubs` behavior. |
| `tests/operators/test_glyphser_config_stubs.py` | Automated test artifact validating `test glyphser config stubs` behavior. |
| `tests/operators/test_glyphser_data_stubs.py` | Automated test artifact validating `test glyphser data stubs` behavior. |
| `tests/operators/test_glyphser_differentialprivacy_stubs.py` | Automated test artifact validating `test glyphser differentialprivacy stubs` behavior. |
| `tests/operators/test_glyphser_error_stubs.py` | Automated test artifact validating `test glyphser error stubs` behavior. |
| `tests/operators/test_glyphser_import_stubs.py` | Automated test artifact validating `test glyphser import stubs` behavior. |
| `tests/operators/test_glyphser_io_stubs.py` | Automated test artifact validating `test glyphser io stubs` behavior. |
| `tests/operators/test_glyphser_model_stubs.py` | Automated test artifact validating `test glyphser model stubs` behavior. |
| `tests/operators/test_glyphser_monitor_stubs.py` | Automated test artifact validating `test glyphser monitor stubs` behavior. |
| `tests/operators/test_glyphser_registry_stubs.py` | Automated test artifact validating `test glyphser registry stubs` behavior. |
| `tests/operators/test_glyphser_tmmu_stubs.py` | Automated test artifact validating `test glyphser tmmu stubs` behavior. |
| `tests/operators/test_glyphser_trace_stubs.py` | Automated test artifact validating `test glyphser trace stubs` behavior. |
| `tests/operators/test_glyphser_tracking_stubs.py` | Automated test artifact validating `test glyphser tracking stubs` behavior. |
| `tests/ops/test_doc_code_separation_gate.py` | Automated test artifact validating `test doc code separation gate` behavior. |
| `tests/ops/test_observability_gate.py` | Automated test artifact validating `test observability gate` behavior. |
| `tests/replay/test_determinism_regression_matrix.py` | Automated test artifact validating `test determinism regression matrix` behavior. |
| `tests/replay/test_replay_divergence.py` | Automated test artifact validating `test replay divergence` behavior. |
| `tests/security/test_authz_and_audit.py` | Automated test artifact validating `test authz and audit` behavior. |
| `tests/security/test_security_baseline_gate.py` | Automated test artifact validating `test security baseline gate` behavior. |
| `tests/storage/test_state_store_recovery.py` | Automated test artifact validating `test state store recovery` behavior. |
| `tests/test_determinism_repeat.py` | Automated test artifact validating `test determinism repeat` behavior. |
| `tests/test_error_codes_manifest.py` | Automated test artifact validating `test error codes manifest` behavior. |
| `tests/test_error_emit.py` | Automated test artifact validating `test error emit` behavior. |
| `tests/test_operator_vectors.py` | Automated test artifact validating `test operator vectors` behavior. |
| `tests/test_replay_binding.py` | Automated test artifact validating `test replay binding` behavior. |
| `tests/test_replay_suite.py` | Automated test artifact validating `test replay suite` behavior. |
| `tests/test_smoke.py` | Automated test artifact validating `test smoke` behavior. |
| `tests/trace/__init__.py` | Automated test artifact validating `init` behavior. |
| `tests/trace/test_compute_trace_hash.py` | Automated test artifact validating `test compute trace hash` behavior. |
| `tests/validation/test_external_validation_gate.py` | Automated test artifact validating `test external validation gate` behavior. |
| `tools/api_cli.py` | Automation or gate script for `api cli` in the push-button pipeline. |
| `tools/api_contract_gate.py` | Automation or gate script for `api contract gate` in the push-button pipeline. |
| `tools/build_operator_registry.py` | Automation or gate script for `build operator registry` in the push-button pipeline. |
| `tools/build_release_bundle.py` | Automation or gate script for `build release bundle` in the push-button pipeline. |
| `tools/codegen/check_generated_drift.py` | Automation or gate script for `check generated drift` in the push-button pipeline. |
| `tools/codegen/clean_build.py` | Automation or gate script for `clean build` in the push-button pipeline. |
| `tools/codegen/clean_build_generate.py` | Automation or gate script for `clean build generate` in the push-button pipeline. |
| `tools/codegen/diff_fidelity.py` | Automation or gate script for `diff fidelity` in the push-button pipeline. |
| `tools/codegen/generate.py` | Automation or gate script for `generate` in the push-button pipeline. |
| `tools/codegen/input_hash_manifest.py` | Automation or gate script for `input hash manifest` in the push-button pipeline. |
| `tools/codegen/run_and_test.py` | Automation or gate script for `run and test` in the push-button pipeline. |
| `tools/codegen/templates/bindings.py.tpl` | Tooling artifact used by project automation for `bindings.py.tpl`. |
| `tools/codegen/templates/error.py.tpl` | Tooling artifact used by project automation for `error.py.tpl`. |
| `tools/codegen/templates/models.py.tpl` | Tooling artifact used by project automation for `models.py.tpl`. |
| `tools/codegen/templates/operators.py.tpl` | Tooling artifact used by project automation for `operators.py.tpl`. |
| `tools/codegen/templates/validators.py.tpl` | Tooling artifact used by project automation for `validators.py.tpl`. |
| `tools/conformance/__init__.py` | Automation or gate script for `init` in the push-button pipeline. |
| `tools/conformance/cli.py` | Automation or gate script for `cli` in the push-button pipeline. |
| `tools/conformance/report_template.json` | Tooling artifact used by project automation for `report_template.json`. |
| `tools/conformance_cli.py` | Automation or gate script for `conformance cli` in the push-button pipeline. |
| `tools/coverage_report.py` | Automation or gate script for `coverage report` in the push-button pipeline. |
| `tools/deploy/deploy_rollback_gate.py` | Automation or gate script for `deploy rollback gate` in the push-button pipeline. |
| `tools/deploy/generate_bundle.py` | Automation or gate script for `generate bundle` in the push-button pipeline. |
| `tools/deploy/generate_env_manifest.py` | Automation or gate script for `generate env manifest` in the push-button pipeline. |
| `tools/deploy/generate_migration_plan.py` | Automation or gate script for `generate migration plan` in the push-button pipeline. |
| `tools/deploy/generate_overlays.py` | Automation or gate script for `generate overlays` in the push-button pipeline. |
| `tools/deploy/overlays/dev.json` | Tooling artifact used by project automation for `dev.json`. |
| `tools/deploy/overlays/prod.json` | Tooling artifact used by project automation for `prod.json`. |
| `tools/deploy/overlays/staging.json` | Tooling artifact used by project automation for `staging.json`. |
| `tools/deploy/run_deployment_pipeline.py` | Automation or gate script for `run deployment pipeline` in the push-button pipeline. |
| `tools/deploy/templates/policy_bindings.json.tpl` | Tooling artifact used by project automation for `policy_bindings.json.tpl`. |
| `tools/deploy/templates/runtime_config.json.tpl` | Tooling artifact used by project automation for `runtime_config.json.tpl`. |
| `tools/deploy/validate_profile.py` | Automation or gate script for `validate profile` in the push-button pipeline. |
| `tools/doc_code_separation_gate.py` | Automation or gate script for `doc code separation gate` in the push-button pipeline. |
| `tools/error_code_gate.py` | Automation or gate script for `error code gate` in the push-button pipeline. |
| `tools/external_validation_gate.py` | Automation or gate script for `external validation gate` in the push-button pipeline. |
| `tools/fixtures_gate.py` | Automation or gate script for `fixtures gate` in the push-button pipeline. |
| `tools/ga_release_gate.py` | Automation or gate script for `ga release gate` in the push-button pipeline. |
| `tools/materialize_doc_artifacts.py` | Automation or gate script for `materialize doc artifacts` in the push-button pipeline. |
| `tools/merge_markdown_to_txt.py` | Automation or gate script for `merge markdown to txt` in the push-button pipeline. |
| `tools/observability_gate.py` | Automation or gate script for `observability gate` in the push-button pipeline. |
| `tools/operator_vectors.py` | Automation or gate script for `operator vectors` in the push-button pipeline. |
| `tools/push_button.py` | Automation or gate script for `push button` in the push-button pipeline. |
| `tools/registry_gate.py` | Automation or gate script for `registry gate` in the push-button pipeline. |
| `tools/release_evidence_gate.py` | Automation or gate script for `release evidence gate` in the push-button pipeline. |
| `tools/reproducibility_check.py` | Automation or gate script for `reproducibility check` in the push-button pipeline. |
| `tools/schema_gate.py` | Automation or gate script for `schema gate` in the push-button pipeline. |
| `tools/security_artifacts.py` | Automation or gate script for `security artifacts` in the push-button pipeline. |
| `tools/security_baseline_gate.py` | Automation or gate script for `security baseline gate` in the push-button pipeline. |
| `tools/spec_lint.py` | Automation or gate script for `spec lint` in the push-button pipeline. |
| `tools/state_recovery_gate.py` | Automation or gate script for `state recovery gate` in the push-button pipeline. |
| `tools/validate_data_integrity.py` | Automation or gate script for `validate data integrity` in the push-button pipeline. |
| `tools/vector_gate.py` | Automation or gate script for `vector gate` in the push-button pipeline. |
| `tools/verify_doc_artifacts.py` | Automation or gate script for `verify doc artifacts` in the push-button pipeline. |
| `tools/verify_release.py` | Automation or gate script for `verify release` in the push-button pipeline. |
| `artifacts/inputs/vectors/catalog.json` | Deterministic vector artifact for `catalog.json` validation. |
| `artifacts/inputs/vectors/checkpoint-restore/vectors-manifest.json` | Deterministic vector artifact for `checkpoint-restore` validation. |
| `artifacts/inputs/vectors/checkpoint-restore/vectors.json` | Deterministic vector artifact for `checkpoint-restore` validation. |
| `artifacts/inputs/vectors/failure-injection/vectors-manifest.json` | Deterministic vector artifact for `failure-injection` validation. |
| `artifacts/inputs/vectors/failure-injection/vectors.json` | Deterministic vector artifact for `failure-injection` validation. |
| `artifacts/inputs/vectors/hello-core/vectors-manifest.json` | Deterministic vector artifact for `hello-core` validation. |
| `artifacts/inputs/vectors/hello-core/vectors.json` | Deterministic vector artifact for `hello-core` validation. |
| `artifacts/inputs/vectors/perf-scale/vectors-manifest.json` | Deterministic vector artifact for `perf-scale` validation. |
| `artifacts/inputs/vectors/perf-scale/vectors.json` | Deterministic vector artifact for `perf-scale` validation. |
| `artifacts/inputs/vectors/registry-lifecycle/vectors-manifest.json` | Deterministic vector artifact for `registry-lifecycle` validation. |
| `artifacts/inputs/vectors/registry-lifecycle/vectors.json` | Deterministic vector artifact for `registry-lifecycle` validation. |
| `artifacts/inputs/vectors/replay-determinism/vectors-manifest.json` | Deterministic vector artifact for `replay-determinism` validation. |
| `artifacts/inputs/vectors/replay-determinism/vectors.json` | Deterministic vector artifact for `replay-determinism` validation. |
| `artifacts/inputs/vectors/replay-suite-1/vectors-manifest.json` | Deterministic vector artifact for `replay-suite-1` validation. |
| `artifacts/inputs/vectors/replay-suite-1/vectors.json` | Deterministic vector artifact for `replay-suite-1` validation. |
| `artifacts/inputs/vectors/replay-suites/index.json` | Deterministic vector artifact for `replay-suites` validation. |
| `artifacts/inputs/vectors/tracking-monitoring/vectors-manifest.json` | Deterministic vector artifact for `tracking-monitoring` validation. |
| `artifacts/inputs/vectors/tracking-monitoring/vectors.json` | Deterministic vector artifact for `tracking-monitoring` validation. |
