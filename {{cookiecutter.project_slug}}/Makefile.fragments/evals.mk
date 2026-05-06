{% if cookiecutter.include_promptfoo == "yes" %}# Makefile.fragments/evals.mk — Prompt evaluation gate (promptfoo)

.PHONY: eval

HAS_PROMPTFOO := $(shell command -v promptfoo >/dev/null 2>&1 && echo yes || echo no)

eval:
ifeq ($(HAS_PROMPTFOO),yes)
	@promptfoo eval --config evals/promptfooconfig.yaml
else
	@echo "WARN: promptfoo not installed; run 'npm install -g promptfoo' to enable eval gate"
	@if [ -n "$$CI" ]; then \
		echo "ERROR: eval gate is required in CI — add 'npm install -g promptfoo' to your workflow"; \
		exit 1; \
	fi
	@echo "WARN: eval gate skipped — install promptfoo to enforce in CI"
endif

{% endif %}