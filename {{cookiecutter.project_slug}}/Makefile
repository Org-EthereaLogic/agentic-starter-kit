# Makefile for {{ cookiecutter.project_name }}
# Layer 5 — external validation. Wraps scripts/* and language tools.
# `make validate` is the canonical pre-merge gate.
#
# Organization: This Makefile includes fragments under Makefile.fragments/
# to reduce duplication and improve maintainability.

SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c

# Include fragment definitions
include Makefile.fragments/defs.mk
include Makefile.fragments/sync.mk
include Makefile.fragments/checks.mk
include Makefile.fragments/python.mk
include Makefile.fragments/typescript.mk
include Makefile.fragments/hooks.mk
include Makefile.fragments/quality.mk
include Makefile.fragments/clean.mk

# Aggregate language-specific targets
.PHONY: lint typecheck test coverage validate help

lint: lint-python lint-typescript
	@echo "lint: complete"

typecheck: typecheck-python typecheck-typescript
	@echo "typecheck: complete"

test: test-python test-typescript
	@echo "test: complete"

coverage: coverage-python coverage-typescript
	@echo "coverage: complete"

validate: governance-review marker-scan governance-check check-traceability check-doc-drift check-action-pins hooks-test lint typecheck test
	@echo "validate: all gates passed"

help:
	@echo "Available targets:"
	@echo "  sync                 Install dependencies (language-specific)"
	@echo "  governance-review    Run the GOV-NNN validator (text output)"
	@echo "  marker-scan          Scan canonical surfaces for stub markers (CRIT-001 / GOV-001)"
	@echo "  governance-check     Verify required files and folders (CRIT-002 / GOV-002..009)"
	@echo "  check-traceability   Validate specs/traceability.json (GOV-010, GOV-011)"
	@echo "  check-doc-drift      Verify path references in docs/specs are real (GOV-012)"
	@echo "  check-action-pins    Warn on float-pinned GitHub Actions \`uses:\` lines (IMP-006)"
	@echo "  hooks-test           Run the runtime-hook regression suite (CRIT-008)"
	@echo "  lint                 Run language linter(s)"
	@echo "  typecheck            Run language type-checker(s)"
	@echo "  test                 Run the test suite"
	@echo "  coverage             Run tests with coverage"
	@echo "  validate             Aggregate gate (the canonical pre-merge check)"
{% if cookiecutter.include_sbom == "yes" %}	@echo "  sbom                 Generate CycloneDX SBOM under sbom/"
{% endif %}{% if cookiecutter.include_codacy == "yes" %}	@echo "  codacy-local         Run Codacy locally (requires codacy-cli)"
{% endif %}{% if cookiecutter.include_snyk == "yes" %}	@echo "  snyk-local           Run Snyk locally (requires snyk CLI)"
{% endif %}	@echo "  clean                Remove caches and build artifacts"
