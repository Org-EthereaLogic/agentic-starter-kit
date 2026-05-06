{% if cookiecutter.include_promptfoo == "yes" %}# Makefile.fragments/evals.mk — Prompt evaluation gate (promptfoo)

.PHONY: eval

HAS_PROMPTFOO := $(shell command -v promptfoo >/dev/null 2>&1 && echo yes || echo no)

eval:
ifeq ($(HAS_PROMPTFOO),yes)
	@promptfoo eval --config evals/promptfooconfig.yaml
else
	@if [ -n "$$CI" ] && [ "$(HAS_NPX)" = "yes" ]; then \
		npx --yes promptfoo eval --config evals/promptfooconfig.yaml; \
	elif [ -n "$$CI" ]; then \
		echo "ERROR: eval gate is required in CI — add Node/npm or promptfoo to your workflow"; \
		exit 1; \
	else \
		echo "WARN: promptfoo not installed; install promptfoo to enable eval gate"; \
		echo "WARN: eval gate skipped — CI still enforces promptfoo when include_promptfoo=yes"; \
	fi
endif

{% endif %}