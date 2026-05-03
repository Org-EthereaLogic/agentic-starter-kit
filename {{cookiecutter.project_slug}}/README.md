# {{ cookiecutter.project_name }}

{{ cookiecutter.project_description }}

---

## Getting Started

**Important:** Before running validation, you must install dependencies:

```sh
git init
git checkout -b feat/initial
make sync         # ← required: install language-specific dependencies
make validate     # run the full pre-merge gate
make hooks-test   # exercise the protected-branch runtime hook
```

- `make sync` installs dev tools (ruff, {{ cookiecutter.python_typechecker }}, pytest, etc.) and must run first
- `make validate` aggregates all governance checks and is the canonical pre-merge gate
- If `make validate` is clean, the scaffold is healthy. Each gate's failure surfaces a specific file or pattern needing attention

## Governance layers

This project ships a **five-layer agentic governance stack**:

| # | Layer | Files |
|---|---|---|
| 1 | Navigation | `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` |
| 2 | Constitutional | `CONSTITUTION.md`, `DIRECTIVES.md`, `SECURITY.md` |
| 3 | Agent specialization | `.claude/agents/*.md`, `.claude/commands/*.md` |
| 4 | Runtime enforcement | `.claude/hooks/pre-tool-use.js`, `.claude/settings.json` |
| 5 | External validation | `Makefile`, `scripts/*.sh`, `.github/workflows/ci.yml` |

Layers are defense in depth — each layer assumes the others might
fail. Read `AGENTS.md` for the operational guardrails and the
required pre-read protocol; `CONSTITUTION.md` for the eight
foundational principles in precedence order; `DIRECTIVES.md` for
the eighteen directives across Critical, Important, and Recommended
classes.

## Layout

| Path | Purpose |
|---|---|
| `CONSTITUTION.md`, `DIRECTIVES.md`, `SECURITY.md` | Constitutional layer (tier 1–3 authority) |
| `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` | Navigation for AI coding tools |
| `.claude/` | Agent specialization (commands, agents, hooks) and runtime enforcement (settings.json + pre-tool-use.js) |
| `Makefile`, `scripts/`, `.github/workflows/` | External validation |
| `tests/` | Test suite, including the runtime-hook regression |
| `docs/` | SWEBOK-anchored documentation (architecture, operations, security program, threat model, …) — populated as the project matures |
| `specs/deep_specs/` | Canonical specs (ADRs, RFCs, designs) |
| `specs/security-requirements/` | Per-feature security requirements |
| `specs/traceability.json` | Machine-readable traceability matrix |
| `report/` | Append-only evidence artifacts (`IMP-001`, `P5`) |

## Required checks

Every substantive change passes the following before commit:

```sh
make marker-scan        # CRIT-001 — no stub markers in canonical surfaces
make governance-check   # CRIT-002 — required files / folders exist
make check-traceability # specs reference real source / tests / evidence
make check-doc-drift    # paths mentioned in docs/ and specs/ exist
make hooks-test         # CRIT-008 — hook regression suite is green
make lint               # language linter
make typecheck          # language type-checker
make test               # test suite
make coverage           # coverage report
make validate           # aggregates the above (the canonical pre-merge gate)
```

CI runs the same gates on every PR. See `.github/workflows/ci.yml`
for the workflow definition.

## License

See [`LICENSE`](./LICENSE).

## Author

{{ cookiecutter.author_name }} <{{ cookiecutter.author_email }}>
