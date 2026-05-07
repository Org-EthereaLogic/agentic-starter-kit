# Template-repository Makefile.
#
# These targets operate on the cookiecutter template source itself.
# The rendered project ships its own Makefile at
# `{{cookiecutter.project_slug}}/Makefile` for downstream use.

PYTHON ?= python3

.PHONY: help template-test template-test-coverage

help:
	@echo "Targets:"
	@echo "  template-test           Run the post-gen hook pruning integration test."
	@echo "  template-test-coverage  Same plus ./coverage.xml in the working dir for Codecov."
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
