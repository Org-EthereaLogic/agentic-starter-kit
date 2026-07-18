# Makefile.fragments/hooks.mk — Hook regression test suite (CRIT-008)
#
# CRIT-008 is enforced at two layers:
#   1. GIT LAYER (primary boundary): .githooks/pre-commit +
#      pre-merge-commit + pre-push, installed via
#      `git config core.hooksPath .githooks` (hooks-install
#      below). They run AFTER shell resolution, so they cannot be dodged
#      by shell idioms (eval, exec, \git, git${IFS}push, bash -cl, sudo,
#      …). Exercised by the language-neutral tests/test_git_hooks.sh,
#      which runs unconditionally (below) regardless of primary_language.
#   2. AGENT LAYER (defense-in-depth): .claude/hooks/pre-tool-use.js, a
#      fast Claude Code PreToolUse:Bash early block. Its py/js regression
#      twins are language-gated below.
#
# Both language paths shell out to `node` to exercise the runtime hook
# (Python via subprocess from the unittest suite; TypeScript via `node
# --test`). Node.js 20+ is the supported floor for the regression
# suite and CI runtime. The hook keeps to broadly supported Node APIs;
# the preflight below is diagnostic only and never aborts the target
# before the tests run.

.PHONY: hooks-install hooks-test

# hooks-install — wire the git-layer CRIT-008 boundary. Idempotent:
# `git config` overwrites the same key, so running it twice is safe.
# `core.hooksPath` makes git use .githooks and ignore .git/hooks, so the
# pre-commit framework's own shim is superseded — the .githooks scripts
# chain to `pre-commit hook-impl` when the framework is present, so its
# hooks keep running (see .githooks/README.md). No-op-safe outside a git
# work tree (prints a note and continues) so `make hooks-test` never
# fails merely because it was invoked from a tarball / fresh render.
hooks-install:
	@if git rev-parse --git-dir >/dev/null 2>&1; then \
		git config core.hooksPath .githooks; \
		echo "hooks-install: core.hooksPath -> .githooks (git-layer CRIT-008 boundary; supersedes 'pre-commit install' via chaining)"; \
	else \
		echo "hooks-install: not a git work tree; skipping core.hooksPath wiring (run 'git init' then 'make hooks-install')"; \
	fi

hooks-test: hooks-install
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
	@# Git-layer CRIT-008 suite — POSIX sh, language-neutral, always runs
	@# (never pruned). Proves the .githooks guards block every shell idiom
	@# that defeats the string-layer hook. Isolated from any ambient git
	@# config so it exercises its own temp repos deterministically.
	env GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null sh tests/test_git_hooks.sh

