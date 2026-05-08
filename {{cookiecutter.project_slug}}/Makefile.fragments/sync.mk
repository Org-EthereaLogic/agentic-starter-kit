# Makefile.fragments/sync.mk — Dependency synchronization targets

.PHONY: sync-python sync-typescript sync

sync-python:
{% if cookiecutter.primary_language in ("python", "polyglot") %}
	@if [ -d .venv ] && ! .venv/bin/python --version >/dev/null 2>&1; then \
		echo "sync-python: removing stale .venv (interpreter is not runnable)"; \
		rm -rf .venv; \
	fi
	@if [ -f pyproject.toml ]; then \
		if [ "$(HAS_UV)" = "yes" ]; then \
			uv sync; \
		elif [ "$(HAS_PIP)" = "yes" ]; then \
			pip install -e .[dev] 2>/dev/null || pip install -e .; \
		else \
			echo "WARN: pyproject.toml present but neither uv nor pip available"; \
		fi; \
	else \
		echo "sync-python: pyproject.toml not present (added in Phase 5)"; \
	fi
{% else %}
	@echo "sync-python: not applicable (Python not in primary_language)"
{% endif %}

sync-typescript:
{% if cookiecutter.primary_language in ("typescript", "polyglot") %}
	@if [ -f package.json ]; then \
		npm install; \
	else \
		echo "sync-typescript: package.json not present (added in Phase 5)"; \
	fi
{% else %}
	@echo "sync-typescript: not applicable (TypeScript not in primary_language)"
{% endif %}

sync: sync-python sync-typescript
	@echo "sync: complete"
