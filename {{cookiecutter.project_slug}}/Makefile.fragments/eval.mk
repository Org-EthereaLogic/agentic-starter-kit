# Makefile.fragments/eval.mk — prompt evaluation gate
#
# `make eval` runs promptfoo against evals/promptfooconfig.yaml when
# include_promptfoo == "yes" was selected at template-render time.
# The default config uses the built-in `echo` provider, so the gate
# is hermetic — no API keys required for the baseline.
#
# Per docs/prompt-versioning-policy.md, every shipped prompt under
# prompts/<name>/vN.md gets at least one assertion-bearing test in
# evals/promptfooconfig.yaml. Threshold breaches return non-zero,
# which propagates through `make eval` to its caller (CI or the
# `validate` aggregate).
#
# This fragment defines the `eval` target only when the user opted
# into promptfoo at template render. When include_promptfoo == "no",
# this file renders empty and `make eval` is undefined; the
# `validate` recipe in the root Makefile uses an `if [ -d evals ]`
# guard so it never invokes a missing target.

{% if cookiecutter.include_promptfoo == "yes" %}.PHONY: eval

eval:
	@if [ -d evals ] && [ -f evals/promptfooconfig.yaml ]; then \
		if command -v promptfoo >/dev/null 2>&1; then \
			promptfoo eval --config evals/promptfooconfig.yaml; \
		elif command -v npx >/dev/null 2>&1; then \
			npx -y promptfoo@0 eval --config evals/promptfooconfig.yaml; \
		else \
			echo "ERROR: neither promptfoo nor npx is available"; \
			echo "       install Node 20+ or run 'npm install -g promptfoo'"; \
			exit 1; \
		fi; \
	else \
		echo "eval: no evals/promptfooconfig.yaml found; nothing to evaluate"; \
	fi
{% endif %}
