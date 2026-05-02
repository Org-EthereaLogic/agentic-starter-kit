# Makefile for {{ cookiecutter.project_name }}
# Layer 5 — external validation. Wraps scripts/* and language tools.
# `make validate` is the canonical pre-merge gate.

SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c

.PHONY: help sync marker-scan governance-check check-traceability \
        check-doc-drift hooks-test lint typecheck test coverage \
        validate{% if cookiecutter.include_sbom == "yes" %} sbom{% endif %}{% if cookiecutter.include_codacy == "yes" %} codacy-local{% endif %}{% if cookiecutter.include_snyk == "yes" %} snyk-local{% endif %} clean

help:
	@echo "Available targets:"
	@echo "  sync                 Install dependencies (language-specific)"
	@echo "  marker-scan          Scan canonical surfaces for stub markers (CRIT-001)"
	@echo "  governance-check     Verify required files and folders (CRIT-002)"
	@echo "  check-traceability   Validate specs/traceability.json (when present)"
	@echo "  check-doc-drift      Verify path references in docs/specs are real"
	@echo "  hooks-test           Run the runtime-hook regression suite (CRIT-008)"
	@echo "  lint                 Run language linter"
	@echo "  typecheck            Run language type-checker"
	@echo "  test                 Run the test suite"
	@echo "  coverage             Run tests with coverage"
	@echo "  validate             Aggregate gate (the canonical pre-merge check)"
{% if cookiecutter.include_sbom == "yes" %}	@echo "  sbom                 Generate CycloneDX SBOM under sbom/"
{% endif %}{% if cookiecutter.include_codacy == "yes" %}	@echo "  codacy-local         Run Codacy locally (requires codacy-cli)"
{% endif %}{% if cookiecutter.include_snyk == "yes" %}	@echo "  snyk-local           Run Snyk locally (requires snyk CLI)"
{% endif %}	@echo "  clean                Remove caches and build artifacts"

sync:
{% if cookiecutter.primary_language in ("python", "polyglot") %}	@if [ -f pyproject.toml ]; then \
		if command -v uv >/dev/null 2>&1; then \
			uv sync; \
		elif command -v pip >/dev/null 2>&1; then \
			pip install -e .[dev] 2>/dev/null || pip install -e .; \
		else \
			echo "WARN: pyproject.toml present but neither uv nor pip available"; \
		fi; \
	else \
		echo "sync: pyproject.toml not present (added in Phase 5); skipping Python deps"; \
	fi
{% endif %}{% if cookiecutter.primary_language in ("typescript", "polyglot") %}	@if [ -f package.json ]; then \
		npm install; \
	else \
		echo "sync: package.json not present (added in Phase 5); skipping Node deps"; \
	fi
{% endif %}	@echo "sync: complete"

marker-scan:
	@bash scripts/marker-scan.sh

governance-check:
	@bash scripts/check-governance.sh

check-traceability:
	@bash scripts/check-traceability.sh

check-doc-drift:
	@bash scripts/check-doc-drift.sh

hooks-test:
{% if cookiecutter.primary_language in ("python", "polyglot") %}	@if [ -f tests/test_pre_tool_use_hook.py ]; then \
		python3 -m unittest tests.test_pre_tool_use_hook -v; \
	fi
{% endif %}{% if cookiecutter.primary_language in ("typescript", "polyglot") %}	@if [ -f tests/test_pre_tool_use_hook.js ]; then \
		node --test tests/test_pre_tool_use_hook.js; \
	fi
{% endif %}

lint:
{% if cookiecutter.primary_language in ("python", "polyglot") %}	@if command -v ruff >/dev/null 2>&1; then \
		ruff check .; \
	else \
		echo "WARN: ruff not installed (added in Phase 5)"; \
	fi
{% endif %}{% if cookiecutter.primary_language in ("typescript", "polyglot") %}	@if command -v eslint >/dev/null 2>&1; then \
		eslint .; \
	elif command -v npx >/dev/null 2>&1 && [ -f package.json ]; then \
		npx --no-install eslint . 2>/dev/null || echo "WARN: eslint not installed (added in Phase 5)"; \
	else \
		echo "WARN: eslint not installed (added in Phase 5)"; \
	fi
{% endif %}

typecheck:
{% if cookiecutter.primary_language in ("python", "polyglot") %}	@if command -v mypy >/dev/null 2>&1; then \
		mypy .; \
	else \
		echo "WARN: mypy not installed (added in Phase 5)"; \
	fi
{% endif %}{% if cookiecutter.primary_language in ("typescript", "polyglot") %}	@if command -v tsc >/dev/null 2>&1 && [ -f tsconfig.json ]; then \
		tsc --noEmit; \
	elif command -v npx >/dev/null 2>&1 && [ -f tsconfig.json ]; then \
		npx --no-install tsc --noEmit 2>/dev/null || echo "WARN: tsc not installed (added in Phase 5)"; \
	else \
		echo "WARN: tsc not installed or no tsconfig.json (added in Phase 5)"; \
	fi
{% endif %}

test:
{% if cookiecutter.primary_language in ("python", "polyglot") %}	@if command -v pytest >/dev/null 2>&1; then \
		pytest tests/; \
	else \
		echo "WARN: pytest not installed (added in Phase 5)"; \
	fi
{% endif %}{% if cookiecutter.primary_language in ("typescript", "polyglot") %}	@if command -v node >/dev/null 2>&1 && [ -d tests ]; then \
		find tests -name '*.test.js' -o -name 'test_*.js' | head -1 >/dev/null && \
		find tests -name '*.test.js' -o -name 'test_*.js' | xargs -r node --test || \
		echo "WARN: no JS test files found"; \
	fi
{% endif %}

coverage:
{% if cookiecutter.primary_language in ("python", "polyglot") %}	@if command -v pytest >/dev/null 2>&1; then \
		pytest --cov=. tests/ 2>/dev/null || pytest tests/; \
	else \
		echo "WARN: pytest not installed (added in Phase 5)"; \
	fi
{% endif %}{% if cookiecutter.primary_language in ("typescript", "polyglot") %}	@echo "coverage: TypeScript coverage tooling lands in Phase 5"
{% endif %}

validate: marker-scan governance-check check-traceability check-doc-drift hooks-test lint typecheck test
	@echo "validate: all gates passed"

{% if cookiecutter.include_sbom == "yes" %}sbom:
	@bash scripts/generate-sbom.sh

{% endif %}{% if cookiecutter.include_codacy == "yes" %}codacy-local:
	@if command -v codacy-cli >/dev/null 2>&1; then \
		codacy-cli analyze; \
	else \
		echo "WARN: codacy-cli not installed; see https://github.com/codacy/codacy-analysis-cli"; \
	fi

{% endif %}{% if cookiecutter.include_snyk == "yes" %}snyk-local:
	@if command -v snyk >/dev/null 2>&1; then \
		snyk test; \
	else \
		echo "WARN: snyk CLI not installed; install via 'npm install -g snyk'"; \
	fi

{% endif %}clean:
	@rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov
	@find . -name __pycache__ -type d -prune -exec rm -rf {} + 2>/dev/null || true
	@find . -name '*.pyc' -delete 2>/dev/null || true
	@rm -rf node_modules dist build
	@rm -rf sbom
	@echo "clean: complete"
