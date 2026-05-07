# Quickstart — {{ cookiecutter.project_name }}

Get up and running in 2 minutes.

## Quick Start

```bash
# 1. Install dependencies (language-specific)
make sync

# 2. Run validation to verify everything works
make validate

# 3. Verify the protected-branch hook is active
make hooks-test
```

That's it! You're ready to start developing.

## Language-Specific Guides

This project supports {% if cookiecutter.primary_language == "python" %}**Python**.{% elif cookiecutter.primary_language == "typescript" %}**TypeScript**.{% else %}**both Python and TypeScript** (polyglot).{% endif %}

{% if cookiecutter.primary_language in ("python", "polyglot") -%}
- **Python developers:** See `QUICKSTART-PYTHON.md`
{% endif -%}
{% if cookiecutter.primary_language in ("typescript", "polyglot") -%}
- **TypeScript developers:** See `QUICKSTART-TYPESCRIPT.md`
{% endif -%}

Before your first push, also skim `KNOWN-ISSUES.md` — it covers
the repo secrets the CI workflow expects, macOS local-dev quirks,
and the kit's tooling defaults.

## Key Commands

### Development

```bash
make lint                 # Run linter
make typecheck            # Run type-checker
make test                 # Run tests
make coverage             # Run tests with coverage
```

### Validation (Pre-Merge Gate)

```bash
make validate             # Run all checks (must pass before merge)
```

The validation gate includes:
- `marker-scan` — No stub markers in canonical surfaces (CRIT-001)
- `governance-check` — Required files exist (CRIT-002)
- `check-doc-drift` — Doc references are real
- `check-traceability` — Specs references are valid
- `hooks-test` — Protected-branch hook works (CRIT-008)
- `lint` — Code style checks
- `typecheck` — Type checking
- `test` — Test suite

### Maintenance

```bash
make clean                # Remove build artifacts and caches
make help                 # Show all available targets
```

## Governance

Your project has **18 governance directives** across 3 severity levels:

- **8 Critical** — Build-breaking rules
- **6 Important** — Merge-blocking rules
- **4 Recommended** — Soft signals for review

View all rules:
```bash
python3 scripts/lib/governance.py --summary
```

The key rules affecting day-to-day work:

| Rule | What it says | Enforcement |
|------|-------------|-------------|
| **CRIT-001** | No `TODO`, `FIXME`, `TBD`, `PLACEHOLDER` in `specs/`, `.claude/`, `docs/` | `make marker-scan` |
| **CRIT-002** | Required governance files exist | `make governance-check` |
| **CRIT-007** | Never use `git commit --no-verify` | Runtime hook |
| **CRIT-008** | Hook test suite passes | `make hooks-test` |
| **IMP-002** | Use conventional commits | Pre-commit hook |
| **IMP-003** | Branch naming: `<type>/<slug>` | Runtime hook |

## Before Committing

**Checklist:**

1. ✓ Run `make validate` — must pass
2. ✓ Use conventional commit format: `feat(scope): description`
3. ✓ Branch named as `<type>/<slug>` (e.g., `feat/auth`)
4. ✓ Stage files explicitly: `git add src/file.py` (never `git add -A`)
5. ✓ Don't use `git commit --no-verify`

## Directory Structure

```
{{ cookiecutter.project_slug }}/
├── README.md                   # Project overview
├── CONTRIBUTING.md             # How to contribute
├── QUICKSTART.md               # This file
{% if cookiecutter.primary_language in ("python", "polyglot") -%}
├── QUICKSTART-PYTHON.md        # Python guide
{% endif -%}
{% if cookiecutter.primary_language in ("typescript", "polyglot") -%}
├── QUICKSTART-TYPESCRIPT.md    # TypeScript guide
{% endif -%}
│
├── src/                        # Your code
├── tests/                      # Your tests
├── docs/                       # Living documentation
├── specs/                      # Specifications
│   └── governance-rules.yaml   # Machine-readable directives
│
├── Makefile                    # Build targets
├── Makefile.fragments/         # Modular Makefile pieces
├── pyproject.toml              # Python config (if applicable)
├── package.json                # Node config (if applicable)
│
├── scripts/                    # Build & validation scripts
│   ├── lib/
│   │   ├── common.sh           # Shared shell utilities
│   │   └── governance.py       # Governance rules loader
│   └── check-*.sh              # Validation scripts
│
└── .claude/                    # Agent & hook configuration
    ├── settings.json           # Hook registration
    └── hooks/pre-tool-use.js   # Protected-branch enforcement
```

## Troubleshooting

### Dependencies not installing

Ensure you're running `make sync` with the correct prerequisites:
- **Python path:** Python 3.11+ and `uv` or `pip`
- **TypeScript path:** Node 20+ with `npm`

### Validation gate failing

Run validation with verbose output:
```bash
# Python
make lint-python
make typecheck-python
make test-python

# TypeScript
make lint-typescript
make typecheck-typescript
make test-typescript

# All checks
make validate
```

### Hook tests failing

The hook regression suite validates the protected-branch enforcement:
```bash
make hooks-test
```

If hook tests fail, check:
```bash
git status              # Are you on a feature branch?
git log -1 --oneline   # Can you see your commits?
```

## Next Steps

1. Pick your language: **Python** or **TypeScript** (or both)
2. Read the relevant quickstart guide
3. Create a feature branch: `git checkout -b feat/your-feature`
4. Write code and tests
5. Run `make validate`
6. Commit and push

## Getting Help

- **Governance questions:** `python3 scripts/lib/governance.py --summary`
- **Contribution guidelines:** `CONTRIBUTING.md`
- **Project philosophy:** `CONSTITUTION.md`
- **Rules & directives:** `DIRECTIVES.md`
- **Security:** `SECURITY.md`
- **Architecture & design:** `docs/` (populated in later phases)

---

Welcome! Happy coding. 🚀
