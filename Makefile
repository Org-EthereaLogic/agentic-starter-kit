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

# Wire the tracked .githooks/pre-push (Tier 1 gate) via core.hooksPath, so a
# fresh clone gets the same gate with one command. Idempotent: `git config`
# overwrites the same key. The hook itself is tracked, not generated here, so
# there is a single source of truth.
install-hooks:
	@git config core.hooksPath .githooks
	@chmod +x .githooks/pre-push 2>/dev/null || true
	@echo "install-hooks: core.hooksPath -> .githooks; pre-push runs the Tier 1 gate (scripts/local-ci/gate.sh)"
