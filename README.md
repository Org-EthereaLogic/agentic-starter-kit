# agentic-starter-kit

A cookiecutter template that scaffolds a new project with a
**five-layer agentic governance stack** wired and tested from
commit zero, plus a complete bridge to **SWEBOK Guide v4.0a**
(September 2025) — Architecture, Software Engineering Operations,
and Software Security.

This template exists for solo operators and small teams running
agentic coding workflows who want governance to be *infrastructure*
(mechanically enforced) rather than *advice* (politely ignored).

For the full philosophy, read [`docs/METHODOLOGY.md`](./docs/METHODOLOGY.md).
For the construction blueprint, read [`docs/BUILD_PLAN.md`](./docs/BUILD_PLAN.md).
For worked examples of what the template produces, read
[`docs/EXAMPLES.md`](./docs/EXAMPLES.md).

---

## What you get

Every project the template scaffolds carries five layers:

| # | Layer | Purpose | Key files |
| --- | --- | --- | --- |
| 1 | Navigation | Tells agents where to look first | `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` |
| 2 | Constitutional | The decision-making contract | `CONSTITUTION.md`, `DIRECTIVES.md`, `SECURITY.md` |
| 3 | Agent specialization | Curated subagents and slash commands | `.claude/agents/*.md`, `.claude/commands/*.md` |
| 4 | Runtime enforcement | Hooks that block bad actions before they happen | `.claude/hooks/pre-tool-use.js`, `.claude/settings.json`, `tests/test_pre_tool_use_hook.{py,js}` |
| 5 | External validation | CI gates that audit independently | `.github/workflows/ci.yml`, `Makefile`, `scripts/*.sh` |

Planned later phases add a complete documentation set anchored to
SWEBOK v4:

- `docs/ARCHITECTURE.md` — IEEE 42010 architecture description with
  named views (logical / process / deployment / data), stakeholders,
  and architecturally-significant decisions cross-referenced to ADRs.
- `docs/OPERATIONS.md` — Operations Plan (capacity, availability,
  backup/recovery, DR, environments, change management) anchored to
  ISO/IEC/IEEE 32675:2022.
- `docs/THREAT_MODEL.md` — STRIDE table with a dedicated ML-specific
  section (model poisoning, evasion, prompt injection) per SWEBOK v4
  Ch 13 §6.3.
- `docs/SECURITY_PROGRAM.md` — DevSecOps lifecycle integration.
- `docs/cert-top-10-compliance.md` — CERT Top 10 self-audit map.
- `docs/sbom-policy.md` — CycloneDX SBOM generation policy.
- `docs/monitoring-strategy.md` — KPIs, telemetry, and alerting.
- `docs/llm-output-verification-rubric.md` — explicit checks for
  fabricated metrics, hallucinated paths, unsupported external state,
  missing citations.

Later phases also add a **machine-readable traceability matrix**
(`specs/traceability.json`, JSON Schema, validator script, CI gate)
that converts "we have specs" into "drift between specs and code is
mechanically detected."

## How to use it

### Prerequisites

- Python 3.10+ (for `cookiecutter` and the post-generation hook)
- `pipx` (recommended) or `pip`
- Node.js 20+ (for the runtime hook and TypeScript path)
- `make`, `git`, `bash`

### Generate a new project

The template is **dual-mode**: render with either
[cookiecutter](https://cookiecutter.readthedocs.io) (one-shot
scaffold) or [copier](https://copier.readthedocs.io) (scaffold
plus an upgrade flow). Both produce structurally identical project
trees from the same variable answers — pick based on whether you
want `copier update` later. See [`docs/UPDATING.md`](./docs/UPDATING.md)
for the upgrade workflow.

#### Option A: copier (recommended — supports `copier update`)

```bash
pipx run copier copy --trust gh:Org-EthereaLogic/agentic-starter-kit ./my-project
```

Or with `pip`:

```bash
pip install --user copier
copier copy --trust gh:Org-EthereaLogic/agentic-starter-kit ./my-project
```

Because this template defines `_tasks` in `copier.yml`, copier asks
you to trust the template before it runs post-render pruning. Pass
`--trust` for unattended runs.

Pulling in later template releases:

```bash
cd ./my-project
copier update --trust --skip-answered
```

If you used `pipx run` for the initial copy and do not want a
persistent install, run the update the same way:

```bash
cd ./my-project
pipx run copier update --trust --skip-answered
```

#### Option B: cookiecutter (one-shot, no upgrade path)

Using `pipx` (recommended — keeps `cookiecutter` isolated):

```bash
pipx run cookiecutter gh:Org-EthereaLogic/agentic-starter-kit
```

Or with `pip`:

```bash
pip install --user cookiecutter
cookiecutter gh:Org-EthereaLogic/agentic-starter-kit
```

Or from a local clone:

```bash
git clone https://github.com/Org-EthereaLogic/agentic-starter-kit.git
cookiecutter ./agentic-starter-kit
```

### Variable surface

Both render modes share the same variable schema — copier's
`copier.yml` mirrors `cookiecutter.json` field-for-field. The
template prompts for the following variables (sensible defaults
shown):

| Variable | Default | Choices | Notes |
| --- | --- | --- | --- |
| `project_name` | `My Agentic Project` | free text | Display name used in narrative documents |
| `project_slug` | derived from `project_name` | derived | Lowercased; dashes replace spaces and underscores |
| `project_description` | `<one-line project description>` | free text | One-line summary used in `pyproject.toml`, `package.json`, README |
| `python_package_name` | derived from `project_slug` | derived | Underscores replace dashes |
| `author_name` | `<your name>` | free text | |
| `author_email` | `<your email>` | free text | Used as the security disclosure address baseline |
| `year` | `2026` | free text | Appears in `LICENSE` and copyright headers |
| `license` | `MIT` | `MIT`, `Apache-2.0`, `Proprietary` | |
| `primary_language` | `python` | `python`, `typescript`, `polyglot` | Drives which build files are kept by the post-gen hook |
| `python_typechecker` | `ty` | `ty`, `mypy` | Astral `ty` is the 2026 default; `mypy` is offered as the opt-in fallback. Affects only the Python and polyglot paths |
| `include_codacy` | `yes` | `yes`, `no` | Adds `.codacy.yml` plus a CI job |
| `include_codecov` | `yes` | `yes`, `no` | Adds `codecov.yaml` plus a CI upload job |
| `include_snyk` | `yes` | `yes`, `no` | Adds `.snyk` plus a CI job |
| `include_sbom` | `yes` | `yes`, `no` | Adds `scripts/generate-sbom.sh` plus a CI job |
| `include_macaron` | `no` | `no`, `yes` | Adds an Oracle Macaron supply-chain analysis job to `supply-chain.yml`. Off by default — Macaron is optional and adds workflow runtime |
| `include_devcontainer` | `yes` | `yes`, `no` | Adds `.devcontainer/devcontainer.json` plus a SHA-pinned multi-stage `Dockerfile` for the rendered project |
| `include_docs_site` | `no` | `no`, `yes` | Adds `mkdocs.yml` (Material theme) and `.github/workflows/docs.yml` that deploys to GitHub Pages on push to the default branch |
| `default_branch_name` | `main` | free text | Protected branch the runtime hook guards |

The post-generation hook (`hooks/post_gen_project.py` for
cookiecutter, `_tasks` in `copier.yml` for copier) removes
language-specific or integration-specific files based on these
answers — for example, `pyproject.toml` is dropped when
`primary_language == typescript` and `.codacy.yml` is dropped when
`include_codacy == no`. Both modes apply the same pruning rules.

### Language toolchain matrix

The `primary_language` choice selects a fixed toolchain. The table
below shows what ships in the rendered project for each path so you
can decide before running the template instead of inspecting
`cookiecutter.json` and the post-gen hook.

| Concern | `python` | `typescript` | `polyglot` |
| --- | --- | --- | --- |
| Build manifest | `pyproject.toml` | `package.json`, `tsconfig.json` | both |
| Package manager | [`uv`](https://docs.astral.sh/uv/) (recommended; `pip` works) | `npm` (Node 20+) | both, side by side |
| Linter | [`ruff`](https://docs.astral.sh/ruff/) | [`eslint`](https://eslint.org/) | both |
| Formatter | `ruff format` | [`prettier`](https://prettier.io/) | both |
| Type checker | [`ty`](https://github.com/astral-sh/ty) (default) or [`mypy`](https://mypy.readthedocs.io/) — selected by `python_typechecker` | `tsc --noEmit` | Python checker per `python_typechecker` **and** `tsc` |
| Test runner | [`pytest`](https://docs.pytest.org/) (`pytest-cov` for coverage) | [`vitest`](https://vitest.dev/) (`@vitest/coverage-v8` for coverage) | both |
| SBOM (when `include_sbom=yes`) | `cyclonedx-py environment` → `sbom/sbom-python.cdx.json` | `@cyclonedx/cyclonedx-npm` → `sbom/sbom-node.cdx.json` | both files emitted |

`polyglot` ships the union: every file listed for `python` *and*
`typescript` survives the post-gen prune, so a polyglot project has
both `pyproject.toml` and `package.json`, both test runners, both
linters, and so on. There is no merged toolchain — the two stacks
co-exist and each owns its own files.

### After generation

```bash
cd <project_slug>
git init
git checkout -b feat/initial
make sync                  # install Python and/or Node deps via pre-commit + pip / npm
make validate              # run all five layers' verification — marker scan,
                           # governance check, traceability, doc drift, hooks test
make governance-review     # run only the GOV-NNN validator (text output)
make hooks-test            # exercise the protected-branch runtime hook test suite
```

`governance-review` (Phase C2, issue #20) emits stable `GOV-NNN`
identifiers anchored to `docs/STANDARDS.md`. Run
`governance-review --list-checks` for the full inventory or
`governance-review --format json` / `--format sarif` for machine-
readable output. The validator is also installable standalone:
`uv tool install ./scripts/governance_review`.

If `make validate` is clean, the scaffold is healthy. If not, every
failure has a fix — the gates are designed to point at the specific
file or pattern needing attention.

## What this template is *not*

- Not a generic project starter. It is opinionated infrastructure
  for agentic workflows.
- Not a framework dependency. The template scaffolds *files*; once
  generated, the project owns its contents and never imports back
  from this template at runtime.
- Not a "best practices" checklist. Every directive is mechanically
  enforced by either a runtime hook or a CI gate. Nothing here is
  aspirational.

## Repository layout

```text
agentic-starter-kit/
├── AGENTS.md                       # Agent guidance for this template repo
├── CLAUDE.md                       # Claude Code quick reference
├── cookiecutter.json               # Variable schema (cookiecutter mode)
├── copier.yml                      # Variable schema + upgrade flow (copier mode)
├── docs/                           # Planning, research, and gap registers
│   ├── METHODOLOGY.md              # The standalone essay
│   ├── BRIEFING.md                 # Build governance for the template
│   ├── BUILD_PLAN.md               # Phased build inventory
│   ├── COMMAND_AND_AGENT_SPECS.md  # New-command/new-agent canonical text
│   ├── SWEBOK_GAP_REGISTER.md      # Source-of-truth gap register
│   └── UPDATING.md                 # `copier update` workflow + locked-file policy
├── .github/
│   └── CODEOWNERS                  # Review ownership routing
├── hooks/
│   └── post_gen_project.py         # Conditional pruning (cookiecutter mode)
├── {{cookiecutter.project_slug}}/  # The templated project tree
│   ├── CLAUDE.md
│   ├── AGENTS.md
│   ├── GEMINI.md
│   ├── CONSTITUTION.md
│   ├── DIRECTIVES.md
│   ├── SECURITY.md
│   ├── README.md
│   ├── METHODOLOGY.md              # Per-project copy of the essay
│   ├── Makefile
│   ├── pyproject.toml              # Python path (conditional)
│   ├── package.json                # TypeScript path (conditional)
│   ├── .claude/
│   │   ├── agents/
│   │   ├── commands/
│   │   ├── hooks/
│   │   └── settings.json
│   ├── .github/
│   │   └── workflows/
│   ├── docs/
│   ├── scripts/
│   ├── specs/
│   │   ├── deep_specs/
│   │   ├── security-requirements/
│   │   ├── traceability.json
│   │   └── traceability.schema.json
│   ├── tests/
│   ├── report/
│   ├── .devcontainer/                  # Devcontainer (conditional)
│   ├── Dockerfile                      # Production image (conditional)
│   └── .dockerignore                   # Production-image ignores (conditional)
├── README.md                       # This file (template-repo manual)
├── LICENSE                         # MIT — for the template repo itself
└── .gitignore
```

## Contributing

The template is governed by the same rules it ships. Authoring
discipline is documented in `docs/BRIEFING.md` (audience: agents and
humans authoring template content). Every PR runs the same
`make validate` gate that the scaffolded projects run.

## Releases and changelog

Tagged releases are listed on [GitHub Releases](https://github.com/Org-EthereaLogic/agentic-starter-kit/releases),
and an offline summary lives in [`CHANGELOG.md`](./CHANGELOG.md).
Generated projects keep their own changelog, maintained automatically
by `release-please` against their own commit history.

## License

The template itself is MIT-licensed (see [`LICENSE`](./LICENSE)). The
license shipped to scaffolded projects is whatever the user selects
at generation time.
