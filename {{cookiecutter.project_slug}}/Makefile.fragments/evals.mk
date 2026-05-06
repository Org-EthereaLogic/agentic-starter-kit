{% if cookiecutter.include_promptfoo == "yes" %}# Makefile.fragments/evals.mk — Prompt evaluation gate (promptfoo)

.PHONY: eval

HAS_PROMPTFOO := $(shell command -v promptfoo >/dev/null 2>&1 && echo yes || echo no)
ifeq ($(HAS_PROMPTFOO),yes)
PROMPTFOO_CMD := promptfoo
else ifeq ($(HAS_NPX),yes)
PROMPTFOO_CMD := npx --yes promptfoo
endif

eval:
ifneq ($(strip $(PROMPTFOO_CMD)),)
	@$(PROMPTFOO_CMD) eval --config evals/promptfooconfig.yaml
else
	@echo "WARN: promptfoo not installed; install promptfoo or npx to enable eval gate"
	@if [ -n "$$CI" ]; then \
		echo "ERROR: eval gate is required in CI — add Node/npm or promptfoo to your workflow"; \
		exit 1; \
	fi
	@echo "WARN: eval gate skipped — install promptfoo or npx to enforce in CI"
endif

{% endif %}