# Template-repository Makefile.
#
# These targets operate on the cookiecutter template source itself.
# The rendered project ships its own Makefile at
# `{{cookiecutter.project_slug}}/Makefile` for downstream use.

PYTHON ?= python3

.PHONY: help template-test template-test-coverage \
        local-ci ci-orb review codacy-local install-hooks

help:
	@echo "Targets:"
	@echo "  template-test           Run the post-gen hook pruning integration test."
	@echo "  template-test-coverage  Same plus ./coverage.xml in the working dir for Codecov."
	@echo
	@echo "Local CI (stand-in for billing-locked GitHub Actions; see scripts/local-ci/README.md):"
	@echo "  local-ci                Tier 1 — fast host gate (pytest + default render smoke)."
	@echo "  ci-orb                  Tier 2 — full cookiecutter+copier render matrix in OrbStack."
	@echo "  review                  Tier 3 — advisory two-model LLM review (Ollama)."
	@echo "  codacy-local            Run the local Codacy CLI (static analysis)."
	@echo "  install-hooks           Install a pre-push hook that runs the Tier 1 gate."
	@echo
	@echo "Requires: cookiecutter, pytest (install via \`pip install cookiecutter pytest\`)."
	@echo "template-test-coverage additionally requires pytest-cov."

template-test:
	$(PYTHON) -m pytest tests/ -v

template-test-coverage:
	$(PYTHON) -m pytest tests/ -v \
	  --cov=hooks \
	  --cov-report=xml \
	  --cov-report=term

# --- Local CI (scripts/local-ci/) -------------------------------------------

local-ci:
	@bash scripts/local-ci/gate.sh

ci-orb:
	@bash scripts/local-ci/orb-ci.sh

review:
	@bash scripts/local-ci/review.sh

# Local static analysis (Codacy CLI). Pin CODACY_CLI_V2_VERSION to avoid the
# per-run "latest release" GitHub API lookup; the binary is cached after the
# first fetch and then runs offline.
codacy-local:
	@bash .codacy/cli.sh analyze

# Install a pre-push hook that runs the Tier 1 gate. Respects a configured
# core.hooksPath (the repo may set it to .githooks); falls back to .git/hooks.
install-hooks:
	@hooks_dir="$$(git config core.hooksPath 2>/dev/null)"; \
	if [ -z "$$hooks_dir" ]; then hooks_dir="$$(git rev-parse --git-path hooks)"; fi; \
	mkdir -p "$$hooks_dir"; \
	printf '#!/bin/sh\nexec bash scripts/local-ci/gate.sh\n' > "$$hooks_dir/pre-push"; \
	chmod +x "$$hooks_dir/pre-push"; \
	echo "install-hooks: pre-push -> scripts/local-ci/gate.sh (in $$hooks_dir)"
