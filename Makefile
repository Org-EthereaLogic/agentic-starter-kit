# Template-repository Makefile.
#
# These targets operate on the cookiecutter template source itself.
# The rendered project ships its own Makefile at
# `{{cookiecutter.project_slug}}/Makefile` for downstream use.

PYTHON ?= python3

.PHONY: help template-test

help:
	@echo "Targets:"
	@echo "  template-test  Run the post-gen hook pruning integration test."
	@echo
	@echo "Requires: cookiecutter, pytest (install via \`pip install cookiecutter pytest\`)"

template-test:
	$(PYTHON) -m pytest tests/ -v
