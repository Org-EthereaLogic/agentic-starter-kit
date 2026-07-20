# Makefile.fragments/defs.mk — Common definitions and helpers

# Common tool predicates
HAS_RUF := $(shell command -v ruff >/dev/null 2>&1 && echo yes || echo no)
HAS_TY := $(shell command -v ty >/dev/null 2>&1 && echo yes || echo no)
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
