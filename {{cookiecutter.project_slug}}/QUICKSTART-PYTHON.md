# Python Quickstart — {{ cookiecutter.project_name }}

Getting started with the Python path of this scaffold.

## Prerequisites

- Python 3.11+
- `uv` package manager (recommended) or `pip`
- `git` 2.40+
- GitHub CLI (`gh`)

## Setup (2 minutes)

```bash
# 1. Install dependencies
make sync

# 2. Run the validation gate to ensure everything works
make validate

# 3. Verify the hook regression suite passes (CRIT-008)
make hooks-test
```

## First commit and CI bring-up

The scaffold is intended to land as a single initial commit, then
push to GitHub for the first CI run. This is the one moment where
`git add -A` is the right call — every file the template produced
is intended.

```bash
# 1. Initialize git on the default branch the runtime hook protects
git init -b {{ cookiecutter.default_branch_name }}

# 2. Stage everything the template produced. After this commit,
#    revert to staging files explicitly (AGENTS.md §Act — IMP-004
#    forbids `git add -A` for normal work).
git add -A

# 3. Install local Git hooks after the repository exists.
uv run pre-commit install --hook-type pre-commit --hook-type pre-push

# 4. Conventional-commit the scaffold. The pre-commit hooks run
#    their configured subset; `make validate` remains the full
#    local verification gate.
git commit -m "chore(scaffold): initial agentic-starter-kit render"

# 5. Create the GitHub repo and push. `--private` is the safer
#    default; flip to `--public` when you're ready to publish.
gh repo create {{ cookiecutter.project_slug }} --private --source=. --push
```

### What to expect on the first CI run

The push triggers `.github/workflows/ci.yml`. Three jobs run by
default; four more run when their toggle was set during render.
OSSF Scorecards runs in `.github/workflows/scorecards.yml`.

| Job | First-run state | Action needed |
| --- | --- | --- |
| `validate` (make validate) | ✅ green | none |
| `hooks-test` (CRIT-008) | ✅ green | none |
| `secret-scan` (TruffleHog OSS) | ✅ green | none — works without a token |
| `sbom` *(if `include_sbom=yes`)* | ✅ green | artifact uploaded |
| `codacy` *(if `include_codacy=yes`)* | ❌ fails | add `CODACY_PROJECT_TOKEN` repo secret |
| `snyk` *(if `include_snyk=yes`)* | ✅ green with warnings | add `SNYK_TOKEN` for complete scan results |
| `codecov` *(if `include_codecov=yes`)* | ✅ green with upload warnings | add `CODECOV_TOKEN` for complete upload results |

Add the missing tokens at **Settings → Secrets and variables →
Actions → New repository secret**:

- `CODACY_PROJECT_TOKEN` — from your Codacy project's *Repositories
  → Settings → Integrations → Project API*.
- `SNYK_TOKEN` — from <https://app.snyk.io/account> (under "Auth
  Token").
- `CODECOV_TOKEN` — from your Codecov repo settings; required even
  for public repos since 2024.

After adding the tokens, re-run the workflow from the GitHub UI.
All enabled jobs should complete, and token-backed integrations
should produce results instead of warnings.

If you opted out of one or more integrations during render, the
corresponding job is absent from the workflow file — there is
nothing to configure.

## Project Structure

```text
{{ cookiecutter.project_slug }}/
├── pyproject.toml              # Python project metadata; dev/prod deps here
├── src/                        # Primary source code
├── tests/                      # Test suite
│   ├── test_pre_tool_use_hook.py  # Hook regression tests (CRIT-008)
│   ├── hook_test_spec.json     # Test specification (single source of truth)
│   └── fixtures/               # Test payloads
├── docs/                       # Living documentation (populated later)
├── specs/                      # Specifications and traceability matrix
├── scripts/                    # Automation scripts
│   ├── lib/
│   │   ├── common.sh           # Shared shell utilities
│   │   └── governance.py       # Governance rules loader
│   └── check-*.sh              # Validation scripts
├── Makefile                    # Build glue; includes Makefile.fragments/
├── Makefile.fragments/         # Modular Makefile organization
├── CONTRIBUTING.md             # Contribution guidelines
└── .claude/                    # Agent configuration
    ├── settings.json           # Hook registration
    └── hooks/
        └── pre-tool-use.js     # Protected-branch enforcement
```

## Common Commands

### Development

```bash
# Run the linter
make lint-python

# Run type-checking
make typecheck-python

# Run tests
make test-python

# Run tests with coverage
make coverage-python
```

### Validation

```bash
# Run a single validation check
make marker-scan              # CRIT-001 — no stub markers
make governance-check         # CRIT-002 — required files exist
make check-doc-drift          # Verify doc path references
make check-traceability       # Validate specs/traceability.json

# Run the full validation gate
make validate                 # All checks in order; this is your pre-merge gate
```

### Build Targets

```bash
# Show all available targets
make help

# Clean build artifacts
make clean
```

## Before Committing

1. **Run validation:**

   ```bash
   make validate
   ```

   All checks must pass before merging to the default branch.

2. **Use conventional commits:**

   ```bash
   git commit -m "feat(auth): add login endpoint"
   ```

   Types: `feat`, `fix`, `refactor`, `chore`, `docs`, `test`, `build`, `ci`, `perf`, `style`

3. **Name your branch:**

   ```bash
   git checkout -b feat/your-feature
   ```

   Format: `<type>/<slug>` (e.g., `feat/auth`, `fix/crash-on-empty-input`)

4. **Stage files explicitly:**

   ```bash
   git add src/auth.py tests/test_auth.py
   ```

   Never use `git add -A` or `git add .`

## Governance Directives

### Critical (Hard Rules — Build Breaks)

- **CRIT-001**: No stub markers (`TODO`, `FIXME`, `TBD`, `PLACEHOLDER`) in `specs/`, `.claude/`, `CLAUDE.md`, `AGENTS.md`, `docs/`
- **CRIT-002**: Required governance files exist (`CONSTITUTION.md`, `DIRECTIVES.md`, `SECURITY.md`, `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `README.md`)
- **CRIT-007**: Never use `--no-verify` on commits
- **CRIT-008**: Hook test suite must pass (`make hooks-test`)

For full directive details, see `DIRECTIVES.md`.

## Testing

### Hook Regression Tests

The hook regression suite validates the protected-branch hook (`CRIT-008`):

```bash
# Run Python hook tests
python3 -m unittest tests.test_pre_tool_use_hook -v

# Or via make
make hooks-test

# Test a single case
python3 -m unittest tests.test_pre_tool_use_hook.PreToolUseHookTests.test_refspec_to_protected_blocks
```

The test specification is in `tests/hook_test_spec.json` — both
language drivers iterate it at import time, so a new case only needs
to be added once. When adding a new test case:

1. Add an entry under `tests` (or `fixtures`) in `hook_test_spec.json`
2. Run `make hooks-test` to verify both implementations pick it up

### Writing Tests

Use `pytest`:

```python
# tests/test_example.py
import pytest

def test_example():
    assert True
```

Run with:

```bash
make test-python
```

## Troubleshooting

### "WARN: ruff not installed"

Ruff is installed as a dev dependency via `pyproject.toml`. Ensure you've run:

```bash
make sync
```

### "WARN: ty not installed" (or "WARN: mypy not installed")

Same as ruff — run `make sync` to install dev dependencies. The
type-checker is selected at template-generation time via the
`python_typechecker` cookiecutter variable. Default is `ty`
(Astral). Projects on `mypy` see the mypy variant of the warning.

### Tests fail but I haven't changed anything

Check that the hook regression tests pass:

```bash
make hooks-test
```

If hook tests fail, the repository may have a stale `.git` state. Verify your branch name and commit setup:

```bash
git status
git log -1 --oneline
```

## Next Steps

1. **Create a feature branch:** `git checkout -b feat/my-feature`
2. **Make changes** in `src/`
3. **Write tests** in `tests/`
4. **Run validation:** `make validate`
5. **Commit with conventional format:** `git commit -m "feat(my-feature): description"`
6. **Push and open a PR**

## Getting Help

- **Governance rules:** `python3 scripts/lib/governance.py --summary`
- **Contribution guidelines:** Read `CONTRIBUTING.md`
- **Project decisions:** See `CONSTITUTION.md` and `DIRECTIVES.md`
- **Architecture:** Check `docs/` (populated in later phases)

---

**Remember:** This scaffold is a template — customize it for your project's needs while preserving the governance boundaries defined in `DIRECTIVES.md`.
