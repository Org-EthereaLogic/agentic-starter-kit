# Makefile.fragments/hooks.mk — Hook regression test suite (CRIT-008)
#
# Both language paths shell out to `node` to exercise the runtime hook
# (Python via subprocess from the unittest suite; TypeScript via `node
# --test`). Node.js 20+ is required because the test runner and the
# hook implementation use APIs introduced in Node 18 / 20. The check
# below is a soft warning — it never fails the target — so users
# without Node still see a clear diagnostic instead of a cryptic
# unittest stack trace or "node: not found".

.PHONY: hooks-test

hooks-test:
	@if ! command -v node >/dev/null 2>&1; then \
		echo "WARN: node not on PATH; the runtime hook regression suite invokes 'node' via subprocess. Install Node.js 20+ to run hooks-test."; \
	else \
		node_major=$$(node --version | sed -E 's/^v([0-9]+).*/\1/'); \
		if [ "$$node_major" -lt 20 ] 2>/dev/null; then \
			echo "WARN: node $$(node --version) is older than the supported floor (20+). hooks-test will run, but behavior is only validated against Node 20+."; \
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
