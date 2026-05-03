# Contributing to {{ cookiecutter.project_name }}

This document is the contributor's quick reference. The
operational source of truth is `AGENTS.md`; the constitutional
authority is `CONSTITUTION.md`; the rules are in `DIRECTIVES.md`.
This file points to those.

---

## First-time setup

```sh
git clone <repo-url>
cd {{ cookiecutter.project_slug }}

# Optional: detect missing tooling and install via your package
# manager. Phase 15 of the upstream template build adds a
# `scripts/bootstrap.sh` that automates this.
{% if cookiecutter.primary_language in ("python", "polyglot") %}
pipx install uv         # or: pip install --user uv
{% endif %}{% if cookiecutter.primary_language in ("typescript", "polyglot") %}
# Node 20+ from your package manager (brew, apt, dnf).
{% endif %}
make sync               # install dependencies (language-specific)
pre-commit install --hook-type pre-commit --hook-type pre-push  # install both local Git hook stages
make validate           # confirm the scaffold is healthy
make hooks-test         # exercise the protected-branch hook
```

If `make validate` is clean, you are ready to contribute.

## Branch and commit conventions

- Branch names follow `<type>/<slug>` (`IMP-003`). Allowed types:
  `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `build`,
  `ci`, `perf`, `style`. Slug is short, kebab-case, and
  descriptive.
- Commit messages follow Conventional Commits (`IMP-002`):
  ```
  <type>(<scope>): <description>

  <optional body>

  <optional footer>
  ```
  Types match the branch types above. Scope is project-defined;
  pick a directory name or a directive ID when applicable.
- **No commits to `{{ cookiecutter.default_branch_name }}` or
  `master`** (`CRIT-008`). The Layer 4 runtime hook
  (`.claude/hooks/pre-tool-use.js`) blocks this. Phase 11 of the
  upstream build verifies the block.
- **No `--no-verify`** (`CRIT-007`). Pre-commit hooks catch
  regressions; bypassing them is a silent quality regression in
  itself.
- **Stage explicitly** (`IMP-004`). Never `git add -A` or
  `git add .`. Stage by file or narrow path glob and review the
  staged set before committing.

## The Plan / Act / Verify / Report loop

Every substantive change runs through this loop. `AGENTS.md` has
the full version; the compressed form:

- **Plan.** Read the pre-read protocol (`AGENTS.md §Pre-read`).
  State scope, contract, acceptance criteria. Name directive IDs
  in play.
- **Act.** Smallest sufficient change (`P6`). Explicit failure
  (`P4`). Stage explicitly (`IMP-004`).
- **Verify.** Run `make validate` locally. Map each acceptance
  criterion to an evidence artifact under `report/`. Mark
  unverified claims `unverified`, never `passed` (`CRIT-005`).
- **Report.** State changed files, outcome, evidence paths.
  Separate measured facts from interpretation.

## Pre-commit + CI

Pre-commit runs on every `git commit`. It executes:

- The `pre-commit-hooks` baseline (whitespace, EOL, large files,
  YAML / JSON / TOML validity, private-key detection).
{% if cookiecutter.primary_language in ("python", "polyglot") %}- `ruff` (lint + format) and `{{ cookiecutter.python_typechecker }}` (type-check) for Python.
{% endif %}{% if cookiecutter.primary_language in ("typescript", "polyglot") %}- `prettier` (format) and `eslint` (lint) for TypeScript.
{% endif %}- `shellcheck` for shell scripts.
- The project's local hooks: `marker-scan` (CRIT-001) and
  `governance-check` (CRIT-002).

CI (`.github/workflows/ci.yml`) runs `make validate` on every PR.
The same set of checks; pre-commit is the local mirror.

To refresh pre-commit hook versions, run:

```sh
pre-commit autoupdate
```

## After a PR merges — `/sync`

Once your PR merges to
`{{ cookiecutter.default_branch_name }}`, run `/sync`:

```sh
# Inside Claude Code:
/sync
```

`/sync` (specified in `.claude/commands/sync.md`, lands in Phase 9
of the upstream build) does the post-merge workspace hygiene
contributors are expected to do anyway: switches to the default
branch, prunes deleted-upstream branches, re-runs `make validate`
on the freshly-merged tip, walks the living docs for drift, and
writes an append-only sync record under `report/`. **Running
`/sync` after every merge is a contributor obligation**, not a
suggestion — the audit trail it creates is what closes the
documentation-drift loop (`GAP-035`).

If `/sync` is not available yet (the slash command lands later in
the build), the manual equivalent is:

```sh
git checkout {{ cookiecutter.default_branch_name }}
git pull --prune
git worktree prune
make sync
make validate
make hooks-test
make check-traceability
```

## Specs and ADRs

Decision-content changes to canonical specs in `specs/deep_specs/`
require `/spec-bump` before edit (`IMP-005`). Substantive changes
to `CONSTITUTION.md`, `DIRECTIVES.md`, or `SECURITY.md` require an
ADR. New features start with a plan spec under
`specs/<type>-<slug>.md` and graduate to `specs/deep_specs/`
once accepted.

## Risk-class autonomy

`CONSTITUTION.md §P8` ties autonomy to risk:

| Risk class | Trigger | Mode |
|---|---|---|
| Low | Docs, tests, refactors with green CI | YOLO |
| Medium | Production-path code or schema change | Auto |
| High | Security, runtime hook, release engineering | Ask |

Contributor obligations scale with the class. A high-risk PR
gets:

- The High-risk checkbox marked in `.github/PULL_REQUEST_TEMPLATE.md`.
- Reviewer attention on the affected directive IDs.
- An evidence artifact under `report/` if the change touches
  Layer 4 / Layer 5 enforcement.

## See also

- `AGENTS.md` — full operational guardrails.
- `CLAUDE.md` / `GEMINI.md` — runtime-specific quick refs.
- `CONSTITUTION.md` — eight principles and the six-tier decision
  order.
- `DIRECTIVES.md` — eighteen directives and their enforcement.
- `SECURITY.md` — disclosure process and agentic-specific scope.
- `docs/METHODOLOGY.md` (template repo) — the standalone essay on
  agentic governance as infrastructure.

---

Questions? Open an issue using the bug, feature, or support
templates under `.github/ISSUE_TEMPLATE/` (the issue-form set
lands in Phase 12 / `GAP-EXT-012`).
