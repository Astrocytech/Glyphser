.PHONY: help release-check test docs-api bench

help:
	@echo "Targets:"
	@echo "  make release-check  # run pre-release validation suite"
	@echo "  make test           # run pytest"
	@echo "  make docs-api       # regenerate API reference"
	@echo "  make bench          # run benchmark harness"

test:
	pytest -q

docs-api:
	python3 tooling/docs/generate_api_reference.py

bench:
	python3 tooling/benchmarks/run_benchmarks.py

release-check: test docs-api bench
	@echo "release-check: PASS"
