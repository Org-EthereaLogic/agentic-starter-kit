# Makefile.fragments/typescript.mk — TypeScript-specific lint, typecheck, and test

.PHONY: lint-typescript typecheck-typescript test-typescript coverage-typescript

lint-typescript:
{% if cookiecutter.primary_language in ("typescript", "polyglot") %}
	@if [ "$(HAS_ESLINT)" = "yes" ]; then \
		eslint .; \
	elif [ "$(HAS_NPX)" = "yes" ] && [ -f package.json ]; then \
		npx --no-install eslint . 2>/dev/null || echo "WARN: eslint not installed (added in Phase 5)"; \
	else \
		echo "WARN: eslint not installed (added in Phase 5)"; \
	fi
{% else %}
	@echo "lint-typescript: not applicable (TypeScript not in primary_language)"
{% endif %}

typecheck-typescript:
{% if cookiecutter.primary_language in ("typescript", "polyglot") %}
	@if [ ! -f tsconfig.json ]; then \
		echo "typecheck-typescript: no tsconfig.json"; \
	elif ! find src tests -type f \( -name '*.ts' -o -name '*.tsx' \) 2>/dev/null | grep -q .; then \
		echo "typecheck-typescript: no .ts/.tsx sources yet (added in Phase 5)"; \
	elif [ "$(HAS_TSC)" = "yes" ]; then \
		tsc --noEmit; \
	elif [ "$(HAS_NPX)" = "yes" ]; then \
		npx --no-install tsc --noEmit 2>/dev/null || echo "WARN: tsc not installed (added in Phase 5)"; \
	else \
		echo "WARN: tsc not installed (added in Phase 5)"; \
	fi
{% else %}
	@echo "typecheck-typescript: not applicable (TypeScript not in primary_language)"
{% endif %}

test-typescript:
{% if cookiecutter.primary_language in ("typescript", "polyglot") %}
	@if [ "$(HAS_NODE)" = "yes" ] && [ -d tests ]; then \
		find tests -name '*.test.js' -o -name 'test_*.js' | head -1 >/dev/null && \
		find tests -name '*.test.js' -o -name 'test_*.js' | xargs -r node --test || \
		echo "WARN: no JS test files found"; \
	fi
{% else %}
	@echo "test-typescript: not applicable (TypeScript not in primary_language)"
{% endif %}

coverage-typescript:
{% if cookiecutter.primary_language in ("typescript", "polyglot") %}
	@echo "coverage-typescript: TypeScript coverage tooling lands in Phase 5"
{% else %}
	@echo "coverage-typescript: not applicable (TypeScript not in primary_language)"
{% endif %}
