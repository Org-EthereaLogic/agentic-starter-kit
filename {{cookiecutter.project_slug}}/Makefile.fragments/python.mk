# Makefile.fragments/python.mk — Python-specific lint, typecheck, and test

.PHONY: lint-python typecheck-python test-python coverage-python

lint-python:
{% if cookiecutter.primary_language in ("python", "polyglot") %}
	@if [ "$(HAS_UV)" = "yes" ]; then \
		uv run --quiet ruff check .; \
	elif [ "$(HAS_RUF)" = "yes" ]; then \
		ruff check .; \
	else \
		echo "WARN: ruff not installed (run 'make sync' or 'uv sync --group dev')"; \
	fi
{% else %}
	@echo "lint-python: not applicable (Python not in primary_language)"
{% endif %}

typecheck-python:
{% if cookiecutter.primary_language in ("python", "polyglot") %}
{% if cookiecutter.python_typechecker == "ty" %}
	@if [ "$(HAS_UV)" = "yes" ]; then \
		uv run --quiet ty check .; \
	elif [ "$(HAS_TY)" = "yes" ]; then \
		ty check .; \
	else \
		echo "WARN: ty not installed (run 'make sync' or 'uv sync --group dev')"; \
	fi
{% else %}
	@if [ "$(HAS_UV)" = "yes" ]; then \
		uv run --quiet mypy .; \
	elif [ "$(HAS_MYPY)" = "yes" ]; then \
		mypy .; \
	else \
		echo "WARN: mypy not installed (run 'make sync' or 'uv sync --group dev')"; \
	fi
{% endif %}
{% else %}
	@echo "typecheck-python: not applicable (Python not in primary_language)"
{% endif %}

test-python:
{% if cookiecutter.primary_language in ("python", "polyglot") %}
	@if [ "$(HAS_UV)" = "yes" ]; then \
		uv run --quiet pytest tests/; \
	elif [ "$(HAS_PYTEST)" = "yes" ]; then \
		pytest tests/; \
	else \
		echo "WARN: pytest not installed (run 'make sync' or 'uv sync --group dev')"; \
	fi
{% else %}
	@echo "test-python: not applicable (Python not in primary_language)"
{% endif %}

coverage-python:
{% if cookiecutter.primary_language in ("python", "polyglot") %}
	@if [ "$(HAS_UV)" = "yes" ]; then \
		if uv run --quiet pytest --help | grep -q -- "--cov"; then \
			uv run --quiet pytest --cov=. tests/; \
		else \
			echo "WARN: pytest-cov not installed; running tests without coverage"; \
			uv run --quiet pytest tests/; \
		fi; \
	elif [ "$(HAS_PYTEST)" = "yes" ]; then \
		if pytest --help | grep -q -- "--cov"; then \
			pytest --cov=. tests/; \
		else \
			echo "WARN: pytest-cov not installed; running tests without coverage"; \
			pytest tests/; \
		fi; \
	else \
		echo "WARN: pytest not installed (run 'make sync' or 'uv sync --group dev')"; \
	fi
{% else %}
	@echo "coverage-python: not applicable (Python not in primary_language)"
{% endif %}
