.PHONY: help release-check test docs-api bench gates traceability evidence-metadata coverage-gates dev-bootstrap lint archive-evidence security-scan

help:
	@echo "Targets:"
	@echo "  make release-check  # run pre-release validation suite"
	@echo "  make test           # run pytest"
	@echo "  make docs-api       # regenerate API reference"
	@echo "  make bench          # run benchmark harness"
	@echo "  make gates          # run quality congruence gates"
	@echo "  make traceability   # generate evidence traceability index"
	@echo "  make evidence-metadata # generate and validate evidence metadata catalog"
	@echo "  make coverage-gates # enforce per-module coverage thresholds from coverage.xml"
	@echo "  make dev-bootstrap  # bootstrap local development environment checks"
	@echo "  make lint           # run static lint/format checks"
	@echo "  make archive-evidence # archive and retain evidence snapshots"
	@echo "  make security-scan  # run security scanners"

test:
	pytest -q

lint:
	ruff check .
	ruff format --check .

docs-api:
	python3 tooling/docs/generate_api_reference.py

bench:
	python3 tooling/benchmarks/run_benchmarks.py
	python3 tooling/benchmarks/variance_impact.py

gates:
	python3 tooling/quality_gates/spec_impl_congruence_gate.py
	python3 tooling/quality_gates/interface_stability_gate.py
	python3 tooling/quality_gates/runtime_tooling_boundary_gate.py
	python3 tooling/quality_gates/determinism_matrix_gate.py
	python3 tooling/quality_gates/schema_evolution_gate.py
	python3 tooling/benchmarks/benchmark_registry_gate.py
	python3 tooling/benchmarks/benchmark_trend_gate.py

traceability:
	python3 tooling/release/generate_traceability_index.py

evidence-metadata:
	python3 tooling/release/generate_evidence_metadata.py
	python3 tooling/quality_gates/evidence_metadata_gate.py

coverage-gates:
	python3 tooling/quality_gates/module_coverage_gate.py --coverage-file coverage.xml

dev-bootstrap:
	python3 tooling/commands/bootstrap_dev.py --verify

archive-evidence:
	python3 tooling/release/archive_evidence.py --keep 10

security-scan:
	bandit -q -r glyphser runtime tooling
	pip-audit

release-check: test docs-api bench gates traceability evidence-metadata archive-evidence
	@echo "release-check: PASS"
