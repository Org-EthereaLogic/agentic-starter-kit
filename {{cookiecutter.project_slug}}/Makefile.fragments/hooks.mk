# Makefile.fragments/hooks.mk — Hook regression test suite (CRIT-008)
#
# Both language paths shell out to `node` to exercise the runtime hook
# (Python via subprocess from the unittest suite; TypeScript via `node
# --test`). Node.js 20+ is the supported floor for the regression
# suite and CI runtime. The hook keeps to broadly supported Node APIs;
# the preflight below is diagnostic only and never aborts the target
# before the tests run.

.PHONY: hooks-test

hooks-test:
	@if ! command -v node >/dev/null 2>&1; then \
		echo "WARN: node not on PATH; the runtime hook regression suite invokes 'node' via subprocess. Install Node.js 20+ to run hooks-test."; \
	else \
		if node_version=$$(node --version 2>/dev/null); then \
			node_major=$$(printf '%s\n' "$$node_version" | sed -E 's/^v([0-9]+).*/\1/'); \
			if [ "$$node_major" -lt 20 ] 2>/dev/null; then \
				echo "WARN: node $$node_version is older than the supported floor (20+). hooks-test will run, but behavior is only validated against Node 20+."; \
			fi; \
		else \
			echo "WARN: node is on PATH but 'node --version' failed. hooks-test will continue and report any runtime failure from the test suite."; \
		fi; \
	fi
{% if cookiecutter.primary_language in ("python", "polyglot") %}
	@if [ -f tests/test_pre_tool_use_hook.py ]; then \
		python3 -m unittest tests.test_pre_tool_use_hook -v; \
	fi
	@if [ -f tests/test_audit_hooks.py ]; then \
		python3 -m unittest tests.test_audit_hooks -v; \
	fi
{% endif %}{% if cookiecutter.primary_language in ("typescript", "polyglot") %}
	@if [ -f tests/test_pre_tool_use_hook.js ]; then \
		node --test tests/test_pre_tool_use_hook.js; \
	fi
	@if [ -f tests/test_audit_hooks.cjs ]; then \
		node --test tests/test_audit_hooks.cjs; \
	fi
{% endif %}
