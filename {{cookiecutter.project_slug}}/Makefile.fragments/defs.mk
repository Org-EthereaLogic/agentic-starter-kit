# Makefile.fragments/defs.mk — Common definitions and helpers

# Common tool predicates
HAS_RUF := $(shell command -v ruff >/dev/null 2>&1 && echo yes || echo no)
HAS_MYPY := $(shell command -v mypy >/dev/null 2>&1 && echo yes || echo no)
HAS_ESLINT := $(shell command -v eslint >/dev/null 2>&1 && echo yes || echo no)
HAS_TSC := $(shell command -v tsc >/dev/null 2>&1 && echo yes || echo no)
HAS_PYTEST := $(shell command -v pytest >/dev/null 2>&1 && echo yes || echo no)
HAS_NPX := $(shell command -v npx >/dev/null 2>&1 && echo yes || echo no)
HAS_NODE := $(shell command -v node >/dev/null 2>&1 && echo yes || echo no)
HAS_UV := $(shell command -v uv >/dev/null 2>&1 && echo yes || echo no)
HAS_PIP := $(shell command -v pip >/dev/null 2>&1 && echo yes || echo no)

# File checks
FILE_PYPROJECT := $(shell [ -f pyproject.toml ] && echo yes || echo no)
FILE_PACKAGE := $(shell [ -f package.json ] && echo yes || echo no)
FILE_TSCONFIG := $(shell [ -f tsconfig.json ] && echo yes || echo no)

# Conditional execution helpers
# Usage: $(call check_tool,ruff,ruff check .,WARN: ruff not installed)
define check_tool
	@if command -v $(1) >/dev/null 2>&1; then $(2); else echo "WARN: $(3)"; fi
endef

# Conditional file checks
# Usage: $(call check_file,pyproject.toml,target to run,message if missing)
define check_file
	@if [ -f $(1) ]; then $(2); else echo "$(3)"; fi
endef
