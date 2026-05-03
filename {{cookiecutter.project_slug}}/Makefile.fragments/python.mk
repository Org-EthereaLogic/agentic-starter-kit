# Makefile.fragments/python.mk — Python-specific lint, typecheck, and test

.PHONY: lint-python typecheck-python test-python coverage-python

lint-python:
{% if cookiecutter.primary_language in ("python", "polyglot") %}
	@if [ "$(HAS_RUF)" = "yes" ]; then \
		ruff check .; \
	else \
		echo "WARN: ruff not installed (added in Phase 5)"; \
	fi
{% else %}
	@echo "lint-python: not applicable (Python not in primary_language)"
{% endif %}

typecheck-python:
{% if cookiecutter.primary_language in ("python", "polyglot") %}
{% if cookiecutter.python_typechecker == "ty" %}
	@if [ "$(HAS_TY)" = "yes" ]; then \
		ty check .; \
	else \
		echo "WARN: ty not installed (added in Phase 5; install via 'uv sync --group dev')"; \
	fi
{% else %}
	@if [ "$(HAS_MYPY)" = "yes" ]; then \
		mypy .; \
	else \
		echo "WARN: mypy not installed (added in Phase 5)"; \
	fi
{% endif %}
{% else %}
	@echo "typecheck-python: not applicable (Python not in primary_language)"
{% endif %}

test-python:
{% if cookiecutter.primary_language in ("python", "polyglot") %}
	@if [ "$(HAS_PYTEST)" = "yes" ]; then \
		pytest tests/; \
	else \
		echo "WARN: pytest not installed (added in Phase 5)"; \
	fi
{% else %}
	@echo "test-python: not applicable (Python not in primary_language)"
{% endif %}

coverage-python:
{% if cookiecutter.primary_language in ("python", "polyglot") %}
	@if [ "$(HAS_PYTEST)" = "yes" ]; then \
		pytest --cov=. tests/ 2>/dev/null || pytest tests/; \
	else \
		echo "WARN: pytest not installed (added in Phase 5)"; \
	fi
{% else %}
	@echo "coverage-python: not applicable (Python not in primary_language)"
{% endif %}
