# TypeScript Quickstart — {{ cookiecutter.project_name }}

Getting started with the TypeScript path of this scaffold.

## Prerequisites

- Node.js 20+ (LTS)
- npm 10+ (comes with Node)
- `git` 2.40+

## Setup (2 minutes)

```bash
# 1. Install dependencies
make sync

# 2. Run the validation gate to ensure everything works
make validate

# 3. Verify the hook regression suite passes (CRIT-008)
make hooks-test
```

## Project Structure

```
{{ cookiecutter.project_slug }}/
├── package.json                # Node project metadata; dev/prod deps here
├── tsconfig.json               # TypeScript configuration
├── src/                        # Primary source code
├── tests/                      # Test suite
│   ├── test_pre_tool_use_hook.js  # Hook regression tests (CRIT-008)
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
        └── pre-tool-use.js     # Agent-layer defense in depth
```

## Common Commands

### Development

```bash
# Run the linter
make lint-typescript

# Run type-checking
make typecheck-typescript

# Run tests
make test-typescript

# Run tests with coverage (framework selection TBD in Phase 5)
make coverage-typescript
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
   git add src/auth.ts tests/test_auth.ts
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
# Run TypeScript hook tests
node --test tests/test_pre_tool_use_hook.js

# Or via make
make hooks-test

# Test a single case
node --test tests/test_pre_tool_use_hook.js --grep "refspec to protected blocks"
```

The test specification is in `tests/hook_test_spec.json` — both
language drivers iterate it at import time, so a new case only needs
to be added once. When adding a new test case:

1. Add an entry under `tests` (or `fixtures`) in `hook_test_spec.json`
2. Run `make hooks-test` to verify both implementations pick it up

### Writing Tests

Use Node's built-in `node:test` module (available in Node 18.0+):

```typescript
// tests/test_example.ts
import test from "node:test";
import assert from "node:assert";

test("example test", () => {
  assert.equal(1 + 1, 2);
});
```

Run with:
```bash
make test-typescript
```

Or directly:
```bash
node --test tests/test_example.ts
```

`npm test` runs the same `node --test` suites over `tests/` (equivalent
to `make test-typescript`), so any of the three commands above exercise
the same file set.

## Troubleshooting

### "WARN: eslint not installed"

ESLint is installed as a dev dependency via `package.json`. Ensure you've run:
```bash
make sync
```

If you prefer, you can run eslint via npx:
```bash
npx eslint .
```

### "WARN: tsc not installed"

TypeScript is installed as a dev dependency. Run `make sync` to install.

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

### Node version issues

Ensure you're using Node 20+ (LTS):
```bash
node --version
```

The scaffold uses ES modules (`"type": "module"` in package.json) and Node's built-in `node:test` module. If you're on an older Node version, upgrade:
```bash
nvm use 20
```
or
```bash
brew upgrade node
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
- **Node.js test framework:** https://nodejs.org/api/test.html

---

**Remember:** This scaffold is a template — customize it for your project's needs while preserving the governance boundaries defined in `DIRECTIVES.md`.
