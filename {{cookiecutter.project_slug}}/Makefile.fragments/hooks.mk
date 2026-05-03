# Makefile.fragments/hooks.mk — Hook regression test suite (CRIT-008)

.PHONY: hooks-test

hooks-test:
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
	@if [ -f tests/test_audit_hooks.js ]; then \
		node --test tests/test_audit_hooks.js; \
	fi
{% endif %}
