# Project File Inventory

Generated: 2026-02-28 16:09:54 UTC

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
│   │   │   ├── clean_build
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
│   │   ├── runtime_state
│   │   │   └── checkpoint-restore
│   │   │       └── ckpt-1.json
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
│   └── release
│       ├── CHECKSUMS_v0.1.0.sha256
│       ├── CHECKSUMS_v0.1.0.sha256.asc
│       ├── RELEASE_NOTES_v0.1.0.md
│       ├── RELEASE_PUBKEY.asc
│       └── SIGNING.md
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
│   ├── security
│   │   ├── audit.log.jsonl
│   │   ├── build_provenance.json
│   │   ├── latest.json
│   │   └── sbom.json
│   ├── structure
│   │   ├── latest.json
│   │   ├── legacy_path_gate.json
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
│   └── structure
│       ├── CANONICAL_CBOR_VECTORS_README.md
│       ├── DOC_CODE_SEPARATION_POLICY.md
│       ├── OPERATOR_STUB_VECTORS_README.txt
│       ├── PHASE1_RESTRUCTURE_MAP.md
│       ├── PHASE2_ARTIFACT_CONSOLIDATION.md
│       ├── PROJECT_FILE_INVENTORY.md
│       └── STRUCTURAL_INVARIANTS.md
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
│   └── site
│       ├── assets
│       │   ├── glyphser3.png
│       │   └── glyphser3.svg
│       ├── services.md
│       └── verify.md
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
│   ├── contracts_docs
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
│   │       ├── Community-Governance-Model.md
│   │       ├── Contracts-Artifact-Lifecycle.md
│   │       ├── Contributing-Workflow.md
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
│   │       ├── PR-Review-Checklist.md
│   │       ├── Profiling-and-Optimization-Guide.md
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
│   │   ├── test_legacy_path_gate.py
│   │   ├── test_observability_gate.py
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
│   ├── codegen
│   │   ├── templates
│   │   │   ├── bindings.py.tpl
│   │   │   ├── error.py.tpl
│   │   │   ├── models.py.tpl
│   │   │   ├── operators.py.tpl
│   │   │   └── validators.py.tpl
│   │   ├── __init__.py
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
│   │   ├── __init__.py
│   │   ├── deploy_rollback_gate.py
│   │   ├── generate_bundle.py
│   │   ├── generate_env_manifest.py
│   │   ├── generate_migration_plan.py
│   │   ├── generate_overlays.py
│   │   ├── run_deployment_pipeline.py
│   │   └── validate_profile.py
│   ├── scripts
│   │   ├── repro
│   │   │   └── host_meta.py
│   │   └── run_hello_core.py
│   ├── __init__.py
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
│   ├── legacy_path_gate.py
│   ├── materialize_doc_artifacts.py
│   ├── merge_markdown_to_txt.py
│   ├── observability_gate.py
│   ├── operator_vectors.py
│   ├── path_config.py
│   ├── push_button.py
│   ├── README.md
│   ├── registry_gate.py
│   ├── release_evidence_gate.py
│   ├── reproducibility_check.py
│   ├── schema_gate.py
│   ├── security_artifacts.py
│   ├── security_baseline_gate.py
│   ├── spec_lint.py
│   ├── state_recovery_gate.py
│   ├── structural_invariants_gate.py
│   ├── validate_data_integrity.py
│   ├── vector_gate.py
│   ├── verify_doc_artifacts.py
│   └── verify_release.py
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

## File Descriptions

| File | Purpose |
| --- | --- |
| `.github/workflows/conformance-gate.yml` | CI workflow automation artifact. |
| `.github/workflows/push-button.yml` | CI workflow automation artifact. |
| `.github/workflows/registry-gate.yml` | CI workflow automation artifact. |
| `.github/workflows/schema-gate.yml` | CI workflow automation artifact. |
| `.gitignore` | Local/repository ignore policy artifact. |
| `CODE_OF_CONDUCT.md` | Repository-level governance/community artifact. |
| `CONTRIBUTING.md` | Repository-level governance/community artifact. |
| `Dockerfile` | Container build artifact. |
| `LICENSE` | Repository-level governance/community artifact. |
| `README.md` | Repository-level governance/community artifact. |
| `SECURITY.md` | Repository-level governance/community artifact. |
| `VERSIONING.md` | Repository-level governance/community artifact. |
| `artifacts/README.md` | Deterministic input/output/generated artifact. |
| `artifacts/__init__.py` | Deterministic input/output/generated artifact. |
| `artifacts/bundles/hello-core-bundle.sha256` | Deterministic input/output/generated artifact. |
| `artifacts/bundles/hello-core-bundle.tar.gz` | Deterministic input/output/generated artifact. |
| `artifacts/expected/goldens/checkpoint-restore/checkpoint_expected.json` | Deterministic input/output/generated artifact. |
| `artifacts/expected/goldens/checkpoint-restore/golden-manifest.json` | Deterministic input/output/generated artifact. |
| `artifacts/expected/goldens/checkpoint-restore/restore_expected.json` | Deterministic input/output/generated artifact. |
| `artifacts/expected/goldens/failure-injection/faulty_expected.json` | Deterministic input/output/generated artifact. |
| `artifacts/expected/goldens/failure-injection/golden-manifest.json` | Deterministic input/output/generated artifact. |
| `artifacts/expected/goldens/golden_inventory.json` | Deterministic input/output/generated artifact. |
| `artifacts/expected/goldens/hello-core/checkpoint_header.json` | Deterministic input/output/generated artifact. |
| `artifacts/expected/goldens/hello-core/execution_certificate.json` | Deterministic input/output/generated artifact. |
| `artifacts/expected/goldens/hello-core/golden-identities.json` | Deterministic input/output/generated artifact. |
| `artifacts/expected/goldens/hello-core/golden-manifest.json` | Deterministic input/output/generated artifact. |
| `artifacts/expected/goldens/hello-core/trace_snippet.json` | Deterministic input/output/generated artifact. |
| `artifacts/expected/goldens/mini-tracking/expected.json` | Deterministic input/output/generated artifact. |
| `artifacts/expected/goldens/perf-scale/forward_expected.json` | Deterministic input/output/generated artifact. |
| `artifacts/expected/goldens/perf-scale/golden-manifest.json` | Deterministic input/output/generated artifact. |
| `artifacts/expected/goldens/registry-lifecycle/golden-manifest.json` | Deterministic input/output/generated artifact. |
| `artifacts/expected/goldens/registry-lifecycle/stage_transition_expected.json` | Deterministic input/output/generated artifact. |
| `artifacts/expected/goldens/registry-lifecycle/version_create_expected.json` | Deterministic input/output/generated artifact. |
| `artifacts/expected/goldens/replay-determinism/golden-manifest.json` | Deterministic input/output/generated artifact. |
| `artifacts/expected/goldens/replay-determinism/replay_expected.json` | Deterministic input/output/generated artifact. |
| `artifacts/expected/goldens/replay-suite-1/golden-manifest.json` | Deterministic input/output/generated artifact. |
| `artifacts/expected/goldens/replay-suite-1/trace_expected.json` | Deterministic input/output/generated artifact. |
| `artifacts/expected/goldens/tracking-monitoring/golden-manifest.json` | Deterministic input/output/generated artifact. |
| `artifacts/expected/goldens/tracking-monitoring/metric_log_expected.json` | Deterministic input/output/generated artifact. |
| `artifacts/generated/__init__.py` | Deterministic input/output/generated artifact. |
| `artifacts/generated/build_metadata/codegen_manifest.json` | Deterministic input/output/generated artifact. |
| `artifacts/generated/build_metadata/input_hashes.json` | Deterministic input/output/generated artifact. |
| `artifacts/generated/codegen/__init__.py` | Deterministic input/output/generated artifact. |
| `artifacts/generated/codegen/bindings.py` | Deterministic input/output/generated artifact. |
| `artifacts/generated/codegen/clean_build/bindings.py` | Deterministic input/output/generated artifact. |
| `artifacts/generated/codegen/clean_build/error.py` | Deterministic input/output/generated artifact. |
| `artifacts/generated/codegen/clean_build/models.py` | Deterministic input/output/generated artifact. |
| `artifacts/generated/codegen/clean_build/operators.py` | Deterministic input/output/generated artifact. |
| `artifacts/generated/codegen/clean_build/validators.py` | Deterministic input/output/generated artifact. |
| `artifacts/generated/codegen/error.py` | Deterministic input/output/generated artifact. |
| `artifacts/generated/codegen/models.py` | Deterministic input/output/generated artifact. |
| `artifacts/generated/codegen/operators.py` | Deterministic input/output/generated artifact. |
| `artifacts/generated/codegen/validators.py` | Deterministic input/output/generated artifact. |
| `artifacts/generated/deploy/confidential/bundle_manifest.json` | Deterministic input/output/generated artifact. |
| `artifacts/generated/deploy/confidential/policy_bindings.json` | Deterministic input/output/generated artifact. |
| `artifacts/generated/deploy/confidential/runtime_config.json` | Deterministic input/output/generated artifact. |
| `artifacts/generated/deploy/env_manifest.json` | Deterministic input/output/generated artifact. |
| `artifacts/generated/deploy/managed/bundle_manifest.json` | Deterministic input/output/generated artifact. |
| `artifacts/generated/deploy/managed/policy_bindings.json` | Deterministic input/output/generated artifact. |
| `artifacts/generated/deploy/managed/runtime_config.json` | Deterministic input/output/generated artifact. |
| `artifacts/generated/deploy/migration_plan.json` | Deterministic input/output/generated artifact. |
| `artifacts/generated/deploy/overlays/dev.json` | Deterministic input/output/generated artifact. |
| `artifacts/generated/deploy/overlays/index.json` | Deterministic input/output/generated artifact. |
| `artifacts/generated/deploy/overlays/prod.json` | Deterministic input/output/generated artifact. |
| `artifacts/generated/deploy/overlays/staging.json` | Deterministic input/output/generated artifact. |
| `artifacts/generated/deploy/regulated/bundle_manifest.json` | Deterministic input/output/generated artifact. |
| `artifacts/generated/deploy/regulated/policy_bindings.json` | Deterministic input/output/generated artifact. |
| `artifacts/generated/deploy/regulated/runtime_config.json` | Deterministic input/output/generated artifact. |
| `artifacts/generated/runtime_state/checkpoint-restore/ckpt-1.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/fixtures/checkpoint-restore/checkpoint_input.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/fixtures/checkpoint-restore/fixture-manifest.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/fixtures/checkpoint-restore/restore_request.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/fixtures/failure-injection/faulty_request.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/fixtures/failure-injection/fixture-manifest.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/fixtures/hello-core/checkpoint.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/fixtures/hello-core/execution_certificate.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/fixtures/hello-core/fixture-manifest.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/fixtures/hello-core/manifest.core.yaml` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/fixtures/hello-core/model_ir.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/fixtures/hello-core/tiny_synth_dataset.jsonl` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/fixtures/hello-core/trace.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/fixtures/mini-tracking/inputs.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/fixtures/perf-scale/batch.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/fixtures/perf-scale/fixture-manifest.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/fixtures/registry-lifecycle/fixture-manifest.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/fixtures/registry-lifecycle/stage_transition.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/fixtures/registry-lifecycle/version_create.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/fixtures/replay-determinism/fixture-manifest.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/fixtures/replay-determinism/trace.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/fixtures/replay-suite-1/fixture-manifest.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/fixtures/replay-suite-1/trace.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/fixtures/tracking-monitoring/fixture-manifest.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/fixtures/tracking-monitoring/run_event.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/catalog.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/checkpoint-restore/vectors-manifest.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/checkpoint-restore/vectors.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/conformance/canonical_cbor/.gitkeep` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/conformance/canonical_cbor/vectors.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/conformance/interface_hash/.gitkeep` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/conformance/interface_hash/vectors.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Backend_LoadDriver.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Certificate_EvidenceValidate.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Checkpoint_CheckpointMigrate.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Checkpoint_Restore.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Config_ManifestMigrate.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Data_NextBatch.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_DifferentialPrivacy_Apply.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Error_Emit.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_IO_SaveCheckpoint.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Import_LegacyFramework.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Model_Forward.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Model_ModelIR_Executor.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Monitor_DriftCompute.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Monitor_Emit.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Monitor_Register.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Registry_StageTransition.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Registry_VersionCreate.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_TMMU_PrepareMemory.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Trace_TraceMigrate.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Tracking_ArtifactGet.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Tracking_ArtifactList.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Tracking_ArtifactPut.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Tracking_ArtifactTombstone.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Tracking_MetricLog.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Tracking_RunCreate.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Tracking_RunEnd.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/conformance/operators/Glyphser_Tracking_RunStart.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/conformance/storage/state_recovery_vectors.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/conformance/struct_validation/.gitkeep` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/conformance/struct_validation/vectors.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/failure-injection/vectors-manifest.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/failure-injection/vectors.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/hello-core/vectors-manifest.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/hello-core/vectors.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/perf-scale/vectors-manifest.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/perf-scale/vectors.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/registry-lifecycle/vectors-manifest.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/registry-lifecycle/vectors.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/replay-determinism/vectors-manifest.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/replay-determinism/vectors.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/replay-suite-1/vectors-manifest.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/replay-suite-1/vectors.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/replay-suites/index.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/tracking-monitoring/vectors-manifest.json` | Deterministic input/output/generated artifact. |
| `artifacts/inputs/vectors/tracking-monitoring/vectors.json` | Deterministic input/output/generated artifact. |
| `distribution/release/CHECKSUMS_v0.1.0.sha256` | Release and distribution artifact. |
| `distribution/release/CHECKSUMS_v0.1.0.sha256.asc` | Release and distribution artifact. |
| `distribution/release/RELEASE_NOTES_v0.1.0.md` | Release and distribution artifact. |
| `distribution/release/RELEASE_PUBKEY.asc` | Release and distribution artifact. |
| `distribution/release/SIGNING.md` | Release and distribution artifact. |
| `docs/BRAND.md` | Entrypoint and orientation documentation artifact. |
| `docs/HELLO_CORE_NEXT_STEPS.md` | Entrypoint and orientation documentation artifact. |
| `docs/START-HERE.md` | Entrypoint and orientation documentation artifact. |
| `docs/VERIFY.md` | Entrypoint and orientation documentation artifact. |
| `evidence/README.md` | Generated verification/report evidence artifact. |
| `evidence/conformance/reports/latest.json` | Generated verification/report evidence artifact. |
| `evidence/conformance/results/latest.json` | Generated verification/report evidence artifact. |
| `evidence/coverage/operator_coverage.json` | Generated verification/report evidence artifact. |
| `evidence/deploy/drift.json` | Generated verification/report evidence artifact. |
| `evidence/deploy/latest.json` | Generated verification/report evidence artifact. |
| `evidence/deploy/parity.json` | Generated verification/report evidence artifact. |
| `evidence/deploy/rollback.json` | Generated verification/report evidence artifact. |
| `evidence/deploy/state/staging_active.json` | Generated verification/report evidence artifact. |
| `evidence/deploy/state/staging_previous.json` | Generated verification/report evidence artifact. |
| `evidence/ga/latest.json` | Generated verification/report evidence artifact. |
| `evidence/ga/release_candidate_verification.json` | Generated verification/report evidence artifact. |
| `evidence/observability/alert_test.json` | Generated verification/report evidence artifact. |
| `evidence/observability/dashboard_inventory.json` | Generated verification/report evidence artifact. |
| `evidence/observability/incident_drill.json` | Generated verification/report evidence artifact. |
| `evidence/observability/latest.json` | Generated verification/report evidence artifact. |
| `evidence/observability/lineage_index.json` | Generated verification/report evidence artifact. |
| `evidence/observability/slo_status.json` | Generated verification/report evidence artifact. |
| `evidence/observability/synthetic_probe.json` | Generated verification/report evidence artifact. |
| `evidence/recovery/backup-restore-drill.json` | Generated verification/report evidence artifact. |
| `evidence/recovery/checkpoint-backup.json` | Generated verification/report evidence artifact. |
| `evidence/recovery/latest.json` | Generated verification/report evidence artifact. |
| `evidence/recovery/replay-proof.txt` | Generated verification/report evidence artifact. |
| `evidence/repro/compare-20260228.md` | Generated verification/report evidence artifact. |
| `evidence/repro/compare-template.md` | Generated verification/report evidence artifact. |
| `evidence/repro/dependency-lock.sha256` | Generated verification/report evidence artifact. |
| `evidence/repro/hashes.txt` | Generated verification/report evidence artifact. |
| `evidence/repro/run-checklist.md` | Generated verification/report evidence artifact. |
| `evidence/security/audit.log.jsonl` | Generated verification/report evidence artifact. |
| `evidence/security/build_provenance.json` | Generated verification/report evidence artifact. |
| `evidence/security/latest.json` | Generated verification/report evidence artifact. |
| `evidence/security/sbom.json` | Generated verification/report evidence artifact. |
| `evidence/structure/latest.json` | Generated verification/report evidence artifact. |
| `evidence/structure/legacy_path_gate.json` | Generated verification/report evidence artifact. |
| `evidence/structure/structural_invariants.json` | Generated verification/report evidence artifact. |
| `evidence/validation/external_security_review.md` | Generated verification/report evidence artifact. |
| `evidence/validation/independent_verification_summary.json` | Generated verification/report evidence artifact. |
| `evidence/validation/issues.json` | Generated verification/report evidence artifact. |
| `evidence/validation/latest.json` | Generated verification/report evidence artifact. |
| `evidence/validation/runs/run-01-linux-mint.json` | Generated verification/report evidence artifact. |
| `evidence/validation/runs/run-02-ubuntu-wsl.json` | Generated verification/report evidence artifact. |
| `evidence/validation/runs/run-03-docs-only-cleanroom.json` | Generated verification/report evidence artifact. |
| `evidence/validation/scorecards/run-01-linux-mint.json` | Generated verification/report evidence artifact. |
| `evidence/validation/scorecards/run-02-ubuntu-wsl.json` | Generated verification/report evidence artifact. |
| `evidence/validation/scorecards/run-03-docs-only-cleanroom.json` | Generated verification/report evidence artifact. |
| `evidence/validation/transcripts/run-01-linux-mint.md` | Generated verification/report evidence artifact. |
| `evidence/validation/transcripts/run-02-ubuntu-wsl.md` | Generated verification/report evidence artifact. |
| `evidence/validation/transcripts/run-03-docs-only-cleanroom.md` | Generated verification/report evidence artifact. |
| `governance/document_guidelines/EquationCode/BRIDGE.md` | Governance, policy, or project control artifact. |
| `governance/document_guidelines/EquationCode/ECOSYSTEM.md` | Governance, policy, or project control artifact. |
| `governance/document_guidelines/EquationCode/EQC.md` | Governance, policy, or project control artifact. |
| `governance/document_guidelines/EquationCode/LICENSE` | Governance, policy, or project control artifact. |
| `governance/document_guidelines/EquationCode/README.md` | Governance, policy, or project control artifact. |
| `governance/ecosystem/ecosystem-compatibility-aggregate.yaml` | Governance, policy, or project control artifact. |
| `governance/ecosystem/ecosystem-graph.yaml` | Governance, policy, or project control artifact. |
| `governance/ecosystem/ecosystem-registry.yaml` | Governance, policy, or project control artifact. |
| `governance/ecosystem/ecosystem-validation-log.md` | Governance, policy, or project control artifact. |
| `governance/ecosystem/ecosystem.md` | Governance, policy, or project control artifact. |
| `governance/ecosystem/tooling-manifest.yaml` | Governance, policy, or project control artifact. |
| `governance/ip/BADGE_PROGRAM_DRAFT.md` | Governance, policy, or project control artifact. |
| `governance/ip/DEFENSIVE_PUBLICATION_PLAN.md` | Governance, policy, or project control artifact. |
| `governance/ip/DISCLOSURE-RULES.md` | Governance, policy, or project control artifact. |
| `governance/ip/IP-POSTURE.md` | Governance, policy, or project control artifact. |
| `governance/lint/semantic_lint_high_confidence.txt` | Governance, policy, or project control artifact. |
| `governance/lint/semantic_lint_report.txt` | Governance, policy, or project control artifact. |
| `governance/registry/data-registry.yaml` | Governance, policy, or project control artifact. |
| `governance/roadmap/INTERPRETATION_LOG.md` | Governance, policy, or project control artifact. |
| `governance/roadmap/WEEKLY_REVIEW_TEMPLATE.md` | Governance, policy, or project control artifact. |
| `governance/roadmap/migration-plan-template.yaml` | Governance, policy, or project control artifact. |
| `governance/roadmap/milestones.txt` | Governance, policy, or project control artifact. |
| `governance/security/OPERATIONS.md` | Governance, policy, or project control artifact. |
| `governance/security/THREAT_MODEL.md` | Governance, policy, or project control artifact. |
| `governance/structure/CANONICAL_CBOR_VECTORS_README.md` | Governance, policy, or project control artifact. |
| `governance/structure/DOC_CODE_SEPARATION_POLICY.md` | Governance, policy, or project control artifact. |
| `governance/structure/OPERATOR_STUB_VECTORS_README.txt` | Governance, policy, or project control artifact. |
| `governance/structure/PHASE1_RESTRUCTURE_MAP.md` | Governance, policy, or project control artifact. |
| `governance/structure/PHASE2_ARTIFACT_CONSOLIDATION.md` | Governance, policy, or project control artifact. |
| `governance/structure/PROJECT_FILE_INVENTORY.md` | Governance, policy, or project control artifact. |
| `governance/structure/STRUCTURAL_INVARIANTS.md` | Governance, policy, or project control artifact. |
| `product/business/DELIVERABLES_LIST.md` | Product/business/ops/public-facing documentation artifact. |
| `product/business/FEES.md` | Product/business/ops/public-facing documentation artifact. |
| `product/business/LOCAL_NETWORK.md` | Product/business/ops/public-facing documentation artifact. |
| `product/business/OFFERS.md` | Product/business/ops/public-facing documentation artifact. |
| `product/business/STRUCTURE_TRACK.md` | Product/business/ops/public-facing documentation artifact. |
| `product/docs/ACCESSIBILITY_REVIEW.md` | Product/business/ops/public-facing documentation artifact. |
| `product/docs/ANNUAL_SECURITY_REVIEW_POLICY.md` | Product/business/ops/public-facing documentation artifact. |
| `product/docs/API_CLI_COMMANDS.md` | Product/business/ops/public-facing documentation artifact. |
| `product/docs/API_LIFECYCLE_POLICY.md` | Product/business/ops/public-facing documentation artifact. |
| `product/docs/API_REFERENCE_v1.md` | Product/business/ops/public-facing documentation artifact. |
| `product/docs/API_STYLE_GUIDE.md` | Product/business/ops/public-facing documentation artifact. |
| `product/docs/CHANGE_COMMUNICATION_SLA.md` | Product/business/ops/public-facing documentation artifact. |
| `product/docs/COMPLIANCE_EVIDENCE_INDEX.md` | Product/business/ops/public-facing documentation artifact. |
| `product/docs/DEPENDENCY_LICENSE_REVIEW.md` | Product/business/ops/public-facing documentation artifact. |
| `product/docs/DOCS_VERSIONING_POLICY.md` | Product/business/ops/public-facing documentation artifact. |
| `product/docs/GA_COMPATIBILITY_GUARANTEES.md` | Product/business/ops/public-facing documentation artifact. |
| `product/docs/GA_CONTRACTUAL_SUPPORT_SLA.md` | Product/business/ops/public-facing documentation artifact. |
| `product/docs/GA_GO_NO_GO_CHECKLIST.md` | Product/business/ops/public-facing documentation artifact. |
| `product/docs/GA_MIGRATION_GUIDE.md` | Product/business/ops/public-facing documentation artifact. |
| `product/docs/GA_RELEASE_TRAIN_POLICY.md` | Product/business/ops/public-facing documentation artifact. |
| `product/docs/GA_SIGNOFF.md` | Product/business/ops/public-facing documentation artifact. |
| `product/docs/GA_STATUS_INCIDENT_COMMUNICATION.md` | Product/business/ops/public-facing documentation artifact. |
| `product/docs/GA_SUPPORT_LIFECYCLE.md` | Product/business/ops/public-facing documentation artifact. |
| `product/docs/GA_SUPPORT_MATRIX.md` | Product/business/ops/public-facing documentation artifact. |
| `product/docs/GA_SUPPORT_OPERATIONS_READINESS.md` | Product/business/ops/public-facing documentation artifact. |
| `product/docs/M17_APPROVAL.md` | Product/business/ops/public-facing documentation artifact. |
| `product/docs/M18_CONTRACT_TEST_REPORT.md` | Product/business/ops/public-facing documentation artifact. |
| `product/docs/M19_RECOVERY_TEST_REPORT.md` | Product/business/ops/public-facing documentation artifact. |
| `product/docs/M20_SECURITY_TEST_REPORT.md` | Product/business/ops/public-facing documentation artifact. |
| `product/docs/M21_DEPLOYMENT_TEST_REPORT.md` | Product/business/ops/public-facing documentation artifact. |
| `product/docs/M22_OBSERVABILITY_REPORT.md` | Product/business/ops/public-facing documentation artifact. |
| `product/docs/M23_EXTERNAL_VALIDATION_REPORT.md` | Product/business/ops/public-facing documentation artifact. |
| `product/docs/M24_GA_RELEASE_REPORT.md` | Product/business/ops/public-facing documentation artifact. |
| `product/docs/PERSISTENCE_SCHEMA_v1.md` | Product/business/ops/public-facing documentation artifact. |
| `product/docs/PERSISTENT_STORAGE_ADAPTER_CONTRACT.md` | Product/business/ops/public-facing documentation artifact. |
| `product/docs/POST_GA_GOVERNANCE.md` | Product/business/ops/public-facing documentation artifact. |
| `product/docs/PRIVACY_IMPACT_ASSESSMENT_WORKFLOW.md` | Product/business/ops/public-facing documentation artifact. |
| `product/docs/PRODUCT_SCOPE.md` | Product/business/ops/public-facing documentation artifact. |
| `product/docs/RUNTIME_PROFILES.md` | Product/business/ops/public-facing documentation artifact. |
| `product/docs/SUPPLY_CHAIN_TRUST_POLICY.md` | Product/business/ops/public-facing documentation artifact. |
| `product/docs/how_to/MILESTONE_15_TWO_HOST_RUNBOOK.md` | Product/business/ops/public-facing documentation artifact. |
| `product/docs/portfolio-release-notes-template.md` | Product/business/ops/public-facing documentation artifact. |
| `product/docs/reports/CONFORMANCE_REPORT_TEMPLATE.md` | Product/business/ops/public-facing documentation artifact. |
| `product/docs/reports/INTEGRATION_REPORT_TEMPLATE.md` | Product/business/ops/public-facing documentation artifact. |
| `product/docs/reports/OUTREACH_2026-02-27.md` | Product/business/ops/public-facing documentation artifact. |
| `product/docs/reports/merged_docs.txt` | Product/business/ops/public-facing documentation artifact. |
| `product/ops/DEPLOYMENT_RUNBOOK.md` | Product/business/ops/public-facing documentation artifact. |
| `product/ops/INCIDENT_RESPONSE.md` | Product/business/ops/public-facing documentation artifact. |
| `product/ops/ROLLBACK_RUNBOOK.md` | Product/business/ops/public-facing documentation artifact. |
| `product/ops/SLOs.md` | Product/business/ops/public-facing documentation artifact. |
| `product/site/assets/glyphser3.png` | Product/business/ops/public-facing documentation artifact. |
| `product/site/assets/glyphser3.svg` | Product/business/ops/public-facing documentation artifact. |
| `product/site/services.md` | Product/business/ops/public-facing documentation artifact. |
| `product/site/verify.md` | Product/business/ops/public-facing documentation artifact. |
| `pyproject.toml` | Build/dependency configuration artifact. |
| `requirements.lock` | Build/dependency configuration artifact. |
| `schemas/SCHEMA_CONVENTIONS.txt` | Machine-readable schema artifact. |
| `schemas/SCHEMA_FORMAT_DECISION.txt` | Machine-readable schema artifact. |
| `schemas/contract_schema_meta.json` | Machine-readable schema artifact. |
| `schemas/l3_operator_error_vectors.schema.json` | Machine-readable schema artifact. |
| `schemas/l3_operator_vectors.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l1_api_interfaces.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l1_canonical_cbor_profile.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l1_data_structures.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l1_dependency_lock_policy.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l1_determinism_profiles.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l1_digest_catalog.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l1_environment_manifest.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l1_error_codes.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l1_normativity_legend.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l1_operator_registry_schema.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l1_redaction_policy.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l2_authz-capability-matrix.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l2_checkpoint-schema.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l2_config-schema.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l2_data-lineage.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l2_data-nextbatch.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l2_deployment-runbook.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l2_differentialprivacy-apply.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l2_evaluation-harness.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l2_execution-certificate.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l2_experiment-tracking.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l2_glyphser-kernel-v3.22-os.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l2_model-registry.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l2_modelir-executor.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l2_monitoring-policy.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l2_pipeline-orchestrator.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l2_replay-determinism.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l2_run-commit-wal.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l2_security-compliance-profile.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l2_tmmu-allocation.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l2_trace-sidecar.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l3_compatibility-test-matrix.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l3_conformance-ci-pipeline.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l3_conformance-harness-guide.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l3_coverage-targets.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l3_data-contract-fuzzing-guide.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l3_failure-injection-index.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l3_failure-injection-scenarios.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l3_game-day-scenarios.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l3_integration-test-matrix.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l3_performance-plan.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l3_release-gates.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l3_storage-recovery-test-matrix.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l3_test-plan.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l3_test-vectors-catalog.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_api-lifecycle-and-deprecation-policy.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_architecture-decisions-log.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_artifact-store-adapter-guide.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_backend-adapter-guide.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_backend-feature-matrix.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_benchmark-evidence-spec.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_brownfield-deployment-guide.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_build-and-ci-matrix.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_canonical-hashing-reference.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_change-control-playbook.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_cli-command-profiles.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_code-generation-mapping.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_coding-standards.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_command-reference.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_common-pitfalls-guide.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_community-governance-model.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_contracts-artifact-lifecycle.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_contributing-workflow.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_debugging-playbook.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_determinism-audit-playbook.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_determinism-debug-checklist.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_deterministic-rng-implementation-guide.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_developer-setup.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_developer-troubleshooting-faq.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_disaster-recovery-operations-runbook.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_distributed-failure-recovery-guide.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_ecosystem-expansion-roadmap.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_eqc-ci-policy.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_evidence-catalog.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_expansion-catalog-041-250.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_external-interface-standard.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_fixtures-and-golden-data.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_formal-verification-roadmap.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_gentle-introduction.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_hello-world-end-to-end-example.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_implementation-backlog.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_implementation-roadmap.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_incident-postmortem-template.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_industry-productization-upgrade-plan.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_interoperability-standards-bridge.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_local-replay-runbook.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_migration-execution-guide.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_module-scaffolding-guide.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_operator-conformance-matrix.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_operator-registry-cbor-contract.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_operator-sdk-scaffold-template.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_pr-review-checklist.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_profiling-and-optimization-guide.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_reference-implementations.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_reference-stack-minimal.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_release-evidence-assembler.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_repo-layout-and-interfaces.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_research-extensions-roadmap.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_runtime-state-machine-reference.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_schema-evolution-playbook.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_scope-and-non-goals.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_sdk-usage-guide.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_security-case-template.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_security-coding-checklist.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_spec-lint-implementation.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_spec-lint-rules.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_sre-incident-triage-playbook.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_test-harness-implementation.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_third-party-operator-certification-program.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_threat-model-and-control-crosswalk.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_tooling-and-automation-suite.schema.json` | Machine-readable schema artifact. |
| `schemas/pilot/l4_tooling-suite.schema.json` | Machine-readable schema artifact. |
| `specs/README.md` | Normative specification or contract artifact. |
| `specs/compatibility/CERTIFICATION_DELIVERABLES.md` | Normative specification or contract artifact. |
| `specs/compatibility/COMPATIBILITY_CRITERIA_v0.1.md` | Normative specification or contract artifact. |
| `specs/compatibility/VENDOR_SELF_TEST_KIT.md` | Normative specification or contract artifact. |
| `specs/contracts/capability_catalog.cbor` | Normative specification or contract artifact. |
| `specs/contracts/catalog-manifest.json` | Normative specification or contract artifact. |
| `specs/contracts/digest_catalog.cbor` | Normative specification or contract artifact. |
| `specs/contracts/error_codes.cbor` | Normative specification or contract artifact. |
| `specs/contracts/error_codes.json` | Normative specification or contract artifact. |
| `specs/contracts/interface_hash.json` | Normative specification or contract artifact. |
| `specs/contracts/openapi_public_api_v1.yaml` | Normative specification or contract artifact. |
| `specs/contracts/operator_registry.cbor` | Normative specification or contract artifact. |
| `specs/contracts/operator_registry.json` | Normative specification or contract artifact. |
| `specs/contracts/operator_registry_source.json` | Normative specification or contract artifact. |
| `specs/contracts/schema_catalog.cbor` | Normative specification or contract artifact. |
| `specs/contracts/vectors_catalog.cbor` | Normative specification or contract artifact. |
| `specs/contracts_docs/COMPATIBILITY_POLICY.md` | Normative specification or contract artifact. |
| `specs/contracts_docs/CONFORMANCE_SUITE_v0.1.md` | Normative specification or contract artifact. |
| `specs/contracts_docs/DETERMINISM_PROFILE_v0.1.md` | Normative specification or contract artifact. |
| `specs/contracts_docs/ERROR_CODES.md` | Normative specification or contract artifact. |
| `specs/contracts_docs/NUMERIC_POLICY_v0.1.md` | Normative specification or contract artifact. |
| `specs/examples/hello-core/hello-core-golden.json` | Normative specification or contract artifact. |
| `specs/examples/hello-core/manifest.core.yaml` | Normative specification or contract artifact. |
| `specs/examples/operators/Glyphser_Backend_LoadDriver.json` | Normative specification or contract artifact. |
| `specs/examples/operators/Glyphser_Certificate_EvidenceValidate.json` | Normative specification or contract artifact. |
| `specs/examples/operators/Glyphser_Checkpoint_CheckpointMigrate.json` | Normative specification or contract artifact. |
| `specs/examples/operators/Glyphser_Checkpoint_Restore.json` | Normative specification or contract artifact. |
| `specs/examples/operators/Glyphser_Config_ManifestMigrate.json` | Normative specification or contract artifact. |
| `specs/examples/operators/Glyphser_Data_NextBatch.json` | Normative specification or contract artifact. |
| `specs/examples/operators/Glyphser_DifferentialPrivacy_Apply.json` | Normative specification or contract artifact. |
| `specs/examples/operators/Glyphser_Error_Emit.json` | Normative specification or contract artifact. |
| `specs/examples/operators/Glyphser_IO_SaveCheckpoint.json` | Normative specification or contract artifact. |
| `specs/examples/operators/Glyphser_Import_LegacyFramework.json` | Normative specification or contract artifact. |
| `specs/examples/operators/Glyphser_Model_Forward.json` | Normative specification or contract artifact. |
| `specs/examples/operators/Glyphser_Model_ModelIR_Executor.json` | Normative specification or contract artifact. |
| `specs/examples/operators/Glyphser_Monitor_DriftCompute.json` | Normative specification or contract artifact. |
| `specs/examples/operators/Glyphser_Monitor_Emit.json` | Normative specification or contract artifact. |
| `specs/examples/operators/Glyphser_Monitor_Register.json` | Normative specification or contract artifact. |
| `specs/examples/operators/Glyphser_Registry_StageTransition.json` | Normative specification or contract artifact. |
| `specs/examples/operators/Glyphser_Registry_VersionCreate.json` | Normative specification or contract artifact. |
| `specs/examples/operators/Glyphser_TMMU_PrepareMemory.json` | Normative specification or contract artifact. |
| `specs/examples/operators/Glyphser_Trace_TraceMigrate.json` | Normative specification or contract artifact. |
| `specs/examples/operators/Glyphser_Tracking_ArtifactGet.json` | Normative specification or contract artifact. |
| `specs/examples/operators/Glyphser_Tracking_ArtifactList.json` | Normative specification or contract artifact. |
| `specs/examples/operators/Glyphser_Tracking_ArtifactPut.json` | Normative specification or contract artifact. |
| `specs/examples/operators/Glyphser_Tracking_ArtifactTombstone.json` | Normative specification or contract artifact. |
| `specs/examples/operators/Glyphser_Tracking_MetricLog.json` | Normative specification or contract artifact. |
| `specs/examples/operators/Glyphser_Tracking_RunCreate.json` | Normative specification or contract artifact. |
| `specs/examples/operators/Glyphser_Tracking_RunEnd.json` | Normative specification or contract artifact. |
| `specs/examples/operators/Glyphser_Tracking_RunStart.json` | Normative specification or contract artifact. |
| `specs/layers/L1-foundation/API-Interfaces.md` | Normative specification or contract artifact. |
| `specs/layers/L1-foundation/Canonical-CBOR-Profile.md` | Normative specification or contract artifact. |
| `specs/layers/L1-foundation/Data-Structures.md` | Normative specification or contract artifact. |
| `specs/layers/L1-foundation/Dependency-Lock-Policy.md` | Normative specification or contract artifact. |
| `specs/layers/L1-foundation/Determinism-Profiles.md` | Normative specification or contract artifact. |
| `specs/layers/L1-foundation/Digest-Catalog.md` | Normative specification or contract artifact. |
| `specs/layers/L1-foundation/Environment-Manifest.md` | Normative specification or contract artifact. |
| `specs/layers/L1-foundation/Error-Codes.md` | Normative specification or contract artifact. |
| `specs/layers/L1-foundation/Normativity-Legend.md` | Normative specification or contract artifact. |
| `specs/layers/L1-foundation/Operator-Registry-Schema.md` | Normative specification or contract artifact. |
| `specs/layers/L1-foundation/Redaction-Policy.md` | Normative specification or contract artifact. |
| `specs/layers/L2-specs/AuthZ-Capability-Matrix.md` | Normative specification or contract artifact. |
| `specs/layers/L2-specs/Checkpoint-Schema.md` | Normative specification or contract artifact. |
| `specs/layers/L2-specs/Config-Schema.md` | Normative specification or contract artifact. |
| `specs/layers/L2-specs/Data-Lineage.md` | Normative specification or contract artifact. |
| `specs/layers/L2-specs/Data-NextBatch.md` | Normative specification or contract artifact. |
| `specs/layers/L2-specs/Deployment-Runbook.md` | Normative specification or contract artifact. |
| `specs/layers/L2-specs/DifferentialPrivacy-Apply.md` | Normative specification or contract artifact. |
| `specs/layers/L2-specs/Evaluation-Harness.md` | Normative specification or contract artifact. |
| `specs/layers/L2-specs/Execution-Certificate.md` | Normative specification or contract artifact. |
| `specs/layers/L2-specs/Experiment-Tracking.md` | Normative specification or contract artifact. |
| `specs/layers/L2-specs/Glyphser-Kernel-v3.22-OS.md` | Normative specification or contract artifact. |
| `specs/layers/L2-specs/Model-Registry.md` | Normative specification or contract artifact. |
| `specs/layers/L2-specs/ModelIR-Executor.md` | Normative specification or contract artifact. |
| `specs/layers/L2-specs/Monitoring-Policy.md` | Normative specification or contract artifact. |
| `specs/layers/L2-specs/Pipeline-Orchestrator.md` | Normative specification or contract artifact. |
| `specs/layers/L2-specs/Replay-Determinism.md` | Normative specification or contract artifact. |
| `specs/layers/L2-specs/Run-Commit-WAL.md` | Normative specification or contract artifact. |
| `specs/layers/L2-specs/Security-Compliance-Profile.md` | Normative specification or contract artifact. |
| `specs/layers/L2-specs/TMMU-Allocation.md` | Normative specification or contract artifact. |
| `specs/layers/L2-specs/Trace-Sidecar.md` | Normative specification or contract artifact. |
| `specs/layers/L3-tests/Compatibility-Test-Matrix.md` | Normative specification or contract artifact. |
| `specs/layers/L3-tests/Conformance-CI-Pipeline.md` | Normative specification or contract artifact. |
| `specs/layers/L3-tests/Conformance-Harness-Guide.md` | Normative specification or contract artifact. |
| `specs/layers/L3-tests/Coverage-Targets.md` | Normative specification or contract artifact. |
| `specs/layers/L3-tests/Data-Contract-Fuzzing-Guide.md` | Normative specification or contract artifact. |
| `specs/layers/L3-tests/Failure-Injection-Index.md` | Normative specification or contract artifact. |
| `specs/layers/L3-tests/Failure-Injection-Scenarios.md` | Normative specification or contract artifact. |
| `specs/layers/L3-tests/Game-Day-Scenarios.md` | Normative specification or contract artifact. |
| `specs/layers/L3-tests/Integration-Test-Matrix.md` | Normative specification or contract artifact. |
| `specs/layers/L3-tests/Operator-Vectors.md` | Normative specification or contract artifact. |
| `specs/layers/L3-tests/Performance-Plan.md` | Normative specification or contract artifact. |
| `specs/layers/L3-tests/Release-Gates.md` | Normative specification or contract artifact. |
| `specs/layers/L3-tests/Storage-Recovery-Test-Matrix.md` | Normative specification or contract artifact. |
| `specs/layers/L3-tests/Test-Coverage-Gaps.md` | Normative specification or contract artifact. |
| `specs/layers/L3-tests/Test-Inventory.md` | Normative specification or contract artifact. |
| `specs/layers/L3-tests/Test-Plan.md` | Normative specification or contract artifact. |
| `specs/layers/L3-tests/Test-Vectors-Catalog.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/API-Lifecycle-and-Deprecation-Policy.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Algorithm-Closure.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Architecture-Decisions-Log.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Artifact-Store-Adapter-Guide.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Backend-Adapter-Guide.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Backend-Feature-Matrix.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Benchmark-Evidence-Spec.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Brownfield-Deployment-Guide.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Build-and-CI-Matrix.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/CLI-Command-Profiles.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Canonical-Hashing-Reference.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Change-Control-Playbook.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Code-Generation-Mapping.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Coding-Standards.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Command-Reference.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Common-Pitfalls-Guide.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Community-Governance-Model.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Contracts-Artifact-Lifecycle.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Contributing-Workflow.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Debugging-Playbook.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Deployment-Generation-Profile.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Determinism-Audit-Playbook.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Determinism-Debug-Checklist.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Deterministic-RNG-Implementation-Guide.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Developer-Setup.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Developer-Troubleshooting-FAQ.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Disaster-Recovery-Operations-Runbook.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Distributed-Failure-Recovery-Guide.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/EQC-CI-Policy.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Ecosystem-Expansion-Roadmap.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Evidence-Catalog.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Expansion-Catalog-041-250.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/External-Interface-Standard.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Fixtures-and-Golden-Data.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Formal-Verification-Roadmap.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Gentle-Introduction.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Hello-World-End-to-End-Example.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Implementation-Backlog.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Implementation-Roadmap.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Incident-Postmortem-Template.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Industry-Productization-Upgrade-Plan.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Interoperability-Standards-Bridge.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Local-Replay-Runbook.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Migration-Execution-Guide.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Module-Scaffolding-Guide.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Operator-Conformance-Matrix.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Operator-Readiness-Checklist.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Operator-Registry-CBOR-Contract.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Operator-SDK-Scaffold-Template.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/PR-Review-Checklist.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Profiling-and-Optimization-Guide.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Reference-Implementations.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Reference-Stack-Minimal.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Release-Evidence-Assembler.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Repo-Layout-and-Interfaces.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Research-Extensions-Roadmap.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Runtime-State-Machine-Reference.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/SDK-Usage-Guide.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/SRE-Incident-Triage-Playbook.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Schema-Evolution-Playbook.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Scope-and-Non-Goals.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Security-Case-Template.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Security-Coding-Checklist.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Spec-Lint-Implementation.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Spec-Lint-Rules.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Target-Architecture-Profile.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Test-Harness-Implementation.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Third-Party-Operator-Certification-Program.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Threat-Model-and-Control-Crosswalk.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Tooling-Suite.md` | Normative specification or contract artifact. |
| `specs/layers/L4-implementation/Tooling-and-Automation-Suite.md` | Normative specification or contract artifact. |
| `src/glyphser/api/runtime_api.py` | Runtime source code artifact. |
| `src/glyphser/api/validate_signature.py` | Runtime source code artifact. |
| `src/glyphser/backend/load_driver.py` | Runtime source code artifact. |
| `src/glyphser/backend/reference_driver.py` | Runtime source code artifact. |
| `src/glyphser/cert/evidence_validate.py` | Runtime source code artifact. |
| `src/glyphser/certificate/build.py` | Runtime source code artifact. |
| `src/glyphser/checkpoint/migrate_checkpoint.py` | Runtime source code artifact. |
| `src/glyphser/checkpoint/restore.py` | Runtime source code artifact. |
| `src/glyphser/checkpoint/write.py` | Runtime source code artifact. |
| `src/glyphser/config/migrate_manifest.py` | Runtime source code artifact. |
| `src/glyphser/contract/validate.py` | Runtime source code artifact. |
| `src/glyphser/data/next_batch.py` | Runtime source code artifact. |
| `src/glyphser/data_structures/validate_struct.py` | Runtime source code artifact. |
| `src/glyphser/dp/apply.py` | Runtime source code artifact. |
| `src/glyphser/error/emit.py` | Runtime source code artifact. |
| `src/glyphser/fingerprint/state_fingerprint.py` | Runtime source code artifact. |
| `src/glyphser/legacy_import/legacy_framework.py` | Runtime source code artifact. |
| `src/glyphser/model/build_grad_dependency_order.py` | Runtime source code artifact. |
| `src/glyphser/model/collect_gradients.py` | Runtime source code artifact. |
| `src/glyphser/model/dispatch_primitive.py` | Runtime source code artifact. |
| `src/glyphser/model/forward.py` | Runtime source code artifact. |
| `src/glyphser/model/ir_schema.py` | Runtime source code artifact. |
| `src/glyphser/model/model_ir_executor.py` | Runtime source code artifact. |
| `src/glyphser/model/topo_sort_nodes.py` | Runtime source code artifact. |
| `src/glyphser/monitor/drift_compute.py` | Runtime source code artifact. |
| `src/glyphser/monitor/emit.py` | Runtime source code artifact. |
| `src/glyphser/monitor/register.py` | Runtime source code artifact. |
| `src/glyphser/registry/interface_hash.py` | Runtime source code artifact. |
| `src/glyphser/registry/registry_builder.py` | Runtime source code artifact. |
| `src/glyphser/registry/stage_transition.py` | Runtime source code artifact. |
| `src/glyphser/registry/version_create.py` | Runtime source code artifact. |
| `src/glyphser/security/__init__.py` | Runtime source code artifact. |
| `src/glyphser/security/audit.py` | Runtime source code artifact. |
| `src/glyphser/security/authz.py` | Runtime source code artifact. |
| `src/glyphser/serialization/canonical_cbor.py` | Runtime source code artifact. |
| `src/glyphser/storage/__init__.py` | Runtime source code artifact. |
| `src/glyphser/storage/state_store.py` | Runtime source code artifact. |
| `src/glyphser/tmmu/commit_execution.py` | Runtime source code artifact. |
| `src/glyphser/tmmu/prepare_memory.py` | Runtime source code artifact. |
| `src/glyphser/trace/compute_trace_hash.py` | Runtime source code artifact. |
| `src/glyphser/trace/migrate_trace.py` | Runtime source code artifact. |
| `src/glyphser/trace/trace_sidecar.py` | Runtime source code artifact. |
| `src/glyphser/tracking/artifact_get.py` | Runtime source code artifact. |
| `src/glyphser/tracking/artifact_list.py` | Runtime source code artifact. |
| `src/glyphser/tracking/artifact_put.py` | Runtime source code artifact. |
| `src/glyphser/tracking/artifact_tombstone.py` | Runtime source code artifact. |
| `src/glyphser/tracking/metric_log.py` | Runtime source code artifact. |
| `src/glyphser/tracking/run_create.py` | Runtime source code artifact. |
| `src/glyphser/tracking/run_end.py` | Runtime source code artifact. |
| `src/glyphser/tracking/run_start.py` | Runtime source code artifact. |
| `tests/__init__.py` | Automated test artifact. |
| `tests/api/__init__.py` | Automated test artifact. |
| `tests/api/test_api_cli.py` | Automated test artifact. |
| `tests/api/test_api_contract_gate.py` | Automated test artifact. |
| `tests/api/test_runtime_api.py` | Automated test artifact. |
| `tests/api/test_validate_signature.py` | Automated test artifact. |
| `tests/canonical_cbor/__init__.py` | Automated test artifact. |
| `tests/canonical_cbor/test_fuzz.py` | Automated test artifact. |
| `tests/canonical_cbor/test_vectors.py` | Automated test artifact. |
| `tests/canonical_cbor/vector_loader.py` | Automated test artifact. |
| `tests/chaos/test_distributed_chaos.py` | Automated test artifact. |
| `tests/conftest.py` | Automated test artifact. |
| `tests/data_structures/__init__.py` | Automated test artifact. |
| `tests/data_structures/test_validate_struct.py` | Automated test artifact. |
| `tests/data_structures/test_vectors.py` | Automated test artifact. |
| `tests/deploy/test_deploy_pipeline_gate.py` | Automated test artifact. |
| `tests/fixtures/test_mini_tracking_fixture.py` | Automated test artifact. |
| `tests/fuzz/test_checkpoint_decode_fuzz.py` | Automated test artifact. |
| `tests/fuzz/test_ir_validation_fuzz.py` | Automated test artifact. |
| `tests/fuzz/test_manifest_parser_fuzz.py` | Automated test artifact. |
| `tests/fuzz/test_schema_parsing_fuzz.py` | Automated test artifact. |
| `tests/fuzz/test_tmmu_planner_invariants.py` | Automated test artifact. |
| `tests/fuzz/test_trace_parser_fuzz.py` | Automated test artifact. |
| `tests/ga/test_ga_release_gate.py` | Automated test artifact. |
| `tests/goldens/test_golden_inventory.py` | Automated test artifact. |
| `tests/interface_hash/__init__.py` | Automated test artifact. |
| `tests/interface_hash/test_vectors.py` | Automated test artifact. |
| `tests/operators/__init__.py` | Automated test artifact. |
| `tests/operators/test_glyphser_backend_stubs.py` | Automated test artifact. |
| `tests/operators/test_glyphser_certificate_stubs.py` | Automated test artifact. |
| `tests/operators/test_glyphser_checkpoint_stubs.py` | Automated test artifact. |
| `tests/operators/test_glyphser_config_stubs.py` | Automated test artifact. |
| `tests/operators/test_glyphser_data_stubs.py` | Automated test artifact. |
| `tests/operators/test_glyphser_differentialprivacy_stubs.py` | Automated test artifact. |
| `tests/operators/test_glyphser_error_stubs.py` | Automated test artifact. |
| `tests/operators/test_glyphser_import_stubs.py` | Automated test artifact. |
| `tests/operators/test_glyphser_io_stubs.py` | Automated test artifact. |
| `tests/operators/test_glyphser_model_stubs.py` | Automated test artifact. |
| `tests/operators/test_glyphser_monitor_stubs.py` | Automated test artifact. |
| `tests/operators/test_glyphser_registry_stubs.py` | Automated test artifact. |
| `tests/operators/test_glyphser_tmmu_stubs.py` | Automated test artifact. |
| `tests/operators/test_glyphser_trace_stubs.py` | Automated test artifact. |
| `tests/operators/test_glyphser_tracking_stubs.py` | Automated test artifact. |
| `tests/ops/test_doc_code_separation_gate.py` | Automated test artifact. |
| `tests/ops/test_legacy_path_gate.py` | Automated test artifact. |
| `tests/ops/test_observability_gate.py` | Automated test artifact. |
| `tests/ops/test_structural_invariants_gate.py` | Automated test artifact. |
| `tests/replay/test_determinism_regression_matrix.py` | Automated test artifact. |
| `tests/replay/test_replay_divergence.py` | Automated test artifact. |
| `tests/security/test_authz_and_audit.py` | Automated test artifact. |
| `tests/security/test_security_baseline_gate.py` | Automated test artifact. |
| `tests/storage/test_state_store_recovery.py` | Automated test artifact. |
| `tests/test_determinism_repeat.py` | Automated test artifact. |
| `tests/test_error_codes_manifest.py` | Automated test artifact. |
| `tests/test_error_emit.py` | Automated test artifact. |
| `tests/test_operator_vectors.py` | Automated test artifact. |
| `tests/test_replay_binding.py` | Automated test artifact. |
| `tests/test_replay_suite.py` | Automated test artifact. |
| `tests/test_smoke.py` | Automated test artifact. |
| `tests/trace/__init__.py` | Automated test artifact. |
| `tests/trace/test_compute_trace_hash.py` | Automated test artifact. |
| `tests/validation/test_external_validation_gate.py` | Automated test artifact. |
| `tooling/README.md` | Automation, gate, or build tooling artifact. |
| `tooling/__init__.py` | Automation, gate, or build tooling artifact. |
| `tooling/api_cli.py` | Automation, gate, or build tooling artifact. |
| `tooling/api_contract_gate.py` | Automation, gate, or build tooling artifact. |
| `tooling/build_operator_registry.py` | Automation, gate, or build tooling artifact. |
| `tooling/build_release_bundle.py` | Automation, gate, or build tooling artifact. |
| `tooling/codegen/__init__.py` | Automation, gate, or build tooling artifact. |
| `tooling/codegen/check_generated_drift.py` | Automation, gate, or build tooling artifact. |
| `tooling/codegen/clean_build.py` | Automation, gate, or build tooling artifact. |
| `tooling/codegen/clean_build_generate.py` | Automation, gate, or build tooling artifact. |
| `tooling/codegen/diff_fidelity.py` | Automation, gate, or build tooling artifact. |
| `tooling/codegen/generate.py` | Automation, gate, or build tooling artifact. |
| `tooling/codegen/input_hash_manifest.py` | Automation, gate, or build tooling artifact. |
| `tooling/codegen/run_and_test.py` | Automation, gate, or build tooling artifact. |
| `tooling/codegen/templates/bindings.py.tpl` | Automation, gate, or build tooling artifact. |
| `tooling/codegen/templates/error.py.tpl` | Automation, gate, or build tooling artifact. |
| `tooling/codegen/templates/models.py.tpl` | Automation, gate, or build tooling artifact. |
| `tooling/codegen/templates/operators.py.tpl` | Automation, gate, or build tooling artifact. |
| `tooling/codegen/templates/validators.py.tpl` | Automation, gate, or build tooling artifact. |
| `tooling/conformance/__init__.py` | Automation, gate, or build tooling artifact. |
| `tooling/conformance/cli.py` | Automation, gate, or build tooling artifact. |
| `tooling/conformance/report_template.json` | Automation, gate, or build tooling artifact. |
| `tooling/conformance_cli.py` | Automation, gate, or build tooling artifact. |
| `tooling/coverage_report.py` | Automation, gate, or build tooling artifact. |
| `tooling/deploy/__init__.py` | Automation, gate, or build tooling artifact. |
| `tooling/deploy/deploy_rollback_gate.py` | Automation, gate, or build tooling artifact. |
| `tooling/deploy/generate_bundle.py` | Automation, gate, or build tooling artifact. |
| `tooling/deploy/generate_env_manifest.py` | Automation, gate, or build tooling artifact. |
| `tooling/deploy/generate_migration_plan.py` | Automation, gate, or build tooling artifact. |
| `tooling/deploy/generate_overlays.py` | Automation, gate, or build tooling artifact. |
| `tooling/deploy/overlays/dev.json` | Automation, gate, or build tooling artifact. |
| `tooling/deploy/overlays/prod.json` | Automation, gate, or build tooling artifact. |
| `tooling/deploy/overlays/staging.json` | Automation, gate, or build tooling artifact. |
| `tooling/deploy/run_deployment_pipeline.py` | Automation, gate, or build tooling artifact. |
| `tooling/deploy/templates/policy_bindings.json.tpl` | Automation, gate, or build tooling artifact. |
| `tooling/deploy/templates/runtime_config.json.tpl` | Automation, gate, or build tooling artifact. |
| `tooling/deploy/validate_profile.py` | Automation, gate, or build tooling artifact. |
| `tooling/doc_code_separation_gate.py` | Automation, gate, or build tooling artifact. |
| `tooling/error_code_gate.py` | Automation, gate, or build tooling artifact. |
| `tooling/external_validation_gate.py` | Automation, gate, or build tooling artifact. |
| `tooling/fixtures_gate.py` | Automation, gate, or build tooling artifact. |
| `tooling/ga_release_gate.py` | Automation, gate, or build tooling artifact. |
| `tooling/legacy_path_gate.py` | Automation, gate, or build tooling artifact. |
| `tooling/materialize_doc_artifacts.py` | Automation, gate, or build tooling artifact. |
| `tooling/merge_markdown_to_txt.py` | Automation, gate, or build tooling artifact. |
| `tooling/observability_gate.py` | Automation, gate, or build tooling artifact. |
| `tooling/operator_vectors.py` | Automation, gate, or build tooling artifact. |
| `tooling/path_config.py` | Automation, gate, or build tooling artifact. |
| `tooling/push_button.py` | Automation, gate, or build tooling artifact. |
| `tooling/registry_gate.py` | Automation, gate, or build tooling artifact. |
| `tooling/release_evidence_gate.py` | Automation, gate, or build tooling artifact. |
| `tooling/reproducibility_check.py` | Automation, gate, or build tooling artifact. |
| `tooling/schema_gate.py` | Automation, gate, or build tooling artifact. |
| `tooling/scripts/repro/host_meta.py` | Automation, gate, or build tooling artifact. |
| `tooling/scripts/run_hello_core.py` | Automation, gate, or build tooling artifact. |
| `tooling/security_artifacts.py` | Automation, gate, or build tooling artifact. |
| `tooling/security_baseline_gate.py` | Automation, gate, or build tooling artifact. |
| `tooling/spec_lint.py` | Automation, gate, or build tooling artifact. |
| `tooling/state_recovery_gate.py` | Automation, gate, or build tooling artifact. |
| `tooling/structural_invariants_gate.py` | Automation, gate, or build tooling artifact. |
| `tooling/validate_data_integrity.py` | Automation, gate, or build tooling artifact. |
| `tooling/vector_gate.py` | Automation, gate, or build tooling artifact. |
| `tooling/verify_doc_artifacts.py` | Automation, gate, or build tooling artifact. |
| `tooling/verify_release.py` | Automation, gate, or build tooling artifact. |
