# {{ cookiecutter.project_name }}

{{ cookiecutter.project_description }}

---

## Getting Started

**Important:** Before running validation, you must install dependencies:

```sh
git init
git checkout -b feat/initial
make sync         # ← required: install language-specific dependencies
make hooks-install # wire the primary protected-branch boundary
make validate     # run the full pre-merge gate
make hooks-test   # exercise git-layer and agent-layer hooks
```

{% if cookiecutter.primary_language == 'python' -%}
- `make sync` installs Python dev tools (`ruff`, `{{ cookiecutter.python_typechecker }}`, `pytest`, etc.) and must run first
{%- elif cookiecutter.primary_language == 'typescript' -%}
- `make sync` installs Node dev tools (`eslint`, `prettier`, `typescript`, etc.) and must run first; tests run via Node's built-in `node --test`, no extra test-runner package required
{%- else -%}
- `make sync` installs dev tools for both stacks — Python (`ruff`, `{{ cookiecutter.python_typechecker }}`, `pytest`) and Node (`eslint`, `prettier`, `typescript`) — and must run first; Node tests run via Node's built-in `node --test`, no extra test-runner package required
{%- endif %}
- `make validate` aggregates all governance checks and is the canonical pre-merge gate
- If `make validate` is clean, the scaffold is healthy. Each gate's failure surfaces a specific file or pattern needing attention

### Quickstart guides

Language-specific on-ramps live alongside the root-level `QUICKSTART.md`
hub. They cover dev-tool install, test/lint/typecheck commands, and a
first-contribution checklist for the variant that ships in this render.

{% if cookiecutter.primary_language == 'python' -%}
- [`QUICKSTART-PYTHON.md`](QUICKSTART-PYTHON.md) — `uv sync`, `pytest`, `ruff`, `{{ cookiecutter.python_typechecker }}`.
{% elif cookiecutter.primary_language == 'typescript' -%}
- [`QUICKSTART-TYPESCRIPT.md`](QUICKSTART-TYPESCRIPT.md) — `npm install`, `node --test`, `eslint`, `tsc`.
{% else -%}
- [`QUICKSTART-PYTHON.md`](QUICKSTART-PYTHON.md) — `uv sync`, `pytest`, `ruff`, `{{ cookiecutter.python_typechecker }}`.
- [`QUICKSTART-TYPESCRIPT.md`](QUICKSTART-TYPESCRIPT.md) — `npm install`, `node --test`, `eslint`, `tsc`.
{% endif %}
{% if cookiecutter.include_devcontainer == 'yes' -%}

### Container workflows

A reproducible dev environment ships in `.devcontainer/devcontainer.json`
(VS Code / GitHub Codespaces). The post-create script installs `uv`,
`jq`, and `ripgrep` on top of the Microsoft devcontainer base image.

A production-grade `Dockerfile` ships at the repo root. It is multi-stage,
runs as a non-root user, and pins its base image by digest. Build it with:

```sh
docker build -t {{ cookiecutter.project_slug }} .
```

Refresh base-image digests via Dependabot's `docker` ecosystem (configured
in `.github/dependabot.yml`).
{% endif -%}
{% if cookiecutter.include_docs_site == 'yes' -%}

### Docs site

A [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) site
surfaces the contents of `docs/`. Preview locally:

```sh
uv tool run --with mkdocs-material mkdocs serve
```

`.github/workflows/docs.yml` builds the site in `--strict` mode on every
pull request and deploys it to GitHub Pages on push to
`{{ cookiecutter.default_branch_name }}`. Enable Pages with source
"GitHub Actions" once the repository exists.
{% endif -%}

## Governance layers

This project ships a **five-layer agentic governance stack**:

| # | Layer | Files |
|---|---|---|
| 1 | Navigation | `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` |
| 2 | Constitutional | `CONSTITUTION.md`, `DIRECTIVES.md`, `SECURITY.md` |
| 3 | Agent specialization | `.claude/agents/*.md`, `.claude/commands/*.md` |
| 4 | Runtime enforcement | `.githooks/*`, `.claude/hooks/pre-tool-use.js`, `.claude/settings.json` |
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
| `.githooks/`, `.claude/` | Primary git-layer enforcement plus agent specialization and defense-in-depth hooks |
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
