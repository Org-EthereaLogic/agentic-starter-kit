# Examples Gallery

Three vignettes that show what the template produces in practice.
Each one names the cookiecutter answers used, lists the files the
render leaves behind, and quotes the canonical `make validate`
output from the resulting tree.

The Day 1 vignettes are reproducible: rerun the command shown and
the inventories should match modulo dependency-version churn. The
Day 7 vignette is illustrative — it shows where a fresh scaffold
typically grows after a week of normal use.

| Vignette | Render mode | Language | Toggles |
| --- | --- | --- | --- |
| [Day 1 — Python project](#day-1--python-project) | cookiecutter, defaults | python | codacy + codecov + snyk + sbom + devcontainer + release-please ON; macaron + docs site OFF |
| [Day 1 — TypeScript project](#day-1--typescript-project) | cookiecutter, `primary_language=typescript` | typescript | same as above |
| [Day 7 — mature project](#day-7--mature-project) | cookiecutter, `primary_language=polyglot` | polyglot | adds mkdocs site + Macaron supply-chain analysis |

Reference paths assume the rendered project root, not the template
repo root.

---

## Day 1 — Python project

### Render command (Python)

```sh
pipx run cookiecutter gh:Org-EthereaLogic/agentic-starter-kit \
  --no-input \
  -o "$TMPDIR/agentic-starter-kit-smoke-py"
```

This accepts every default in `cookiecutter.json`: Python primary
language, Astral `ty` typechecker, MIT license, devcontainer +
release automation on, Macaron + docs site off.

The post-generation hook reports what it pruned:

```text
Pruning unselected files…
  removed package.json
  removed tsconfig.json
  removed tests/test_pre_tool_use_hook.js
  removed .claude/agents/typescript-pro.md
  removed mkdocs.yml
  removed docs/index.md
  removed .github/workflows/docs.yml
  removed .copier-answers.yml

Project scaffolded successfully.
  primary_language : python
  python_typecheck : ty
  license          : MIT
  codacy           : yes
  codecov          : yes
  snyk             : yes
  sbom             : yes
  macaron          : no
  devcontainer     : yes
  docs site        : no
  release autom.   : yes
```

### File inventory

118 files spanning all five governance layers.

```text
my-agentic-project/
├── AGENTS.md                           # Layer 1 — navigation
├── CLAUDE.md
├── GEMINI.md
├── CONSTITUTION.md                     # Layer 2 — constitutional foundation
├── DIRECTIVES.md
├── SECURITY.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── QUICKSTART.md                       # plus per-language QUICKSTART-PYTHON.md
├── QUICKSTART-PYTHON.md
├── QUICKSTART-TYPESCRIPT.md            #   (kept as cross-reference)
├── pyproject.toml                      # Python build glue
├── governance-rules.yaml               # canonical rule manifest
├── codecov.yaml                        # coverage upload config
├── release-please-config.json          # release automation
├── release-please-manifest.json
├── .codacy.yml                         # quality gate
├── .snyk                               # security gate
├── .cz.toml                            # commitizen
├── .editorconfig
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── .dockerignore
├── .mcp.json                           # MCP server policy
├── Dockerfile                          # production image
├── Makefile                            # Layer 5 — external validation
├── Makefile.fragments/                 # 8 fragment files
│   ├── checks.mk
│   ├── clean.mk
│   ├── defs.mk
│   ├── hooks.mk
│   ├── python.mk
│   ├── quality.mk
│   ├── sync.mk
│   └── typescript.mk
├── .claude/                            # Layer 3 — agents + Layer 4 — hooks
│   ├── agents/                         # 7 agents (typescript-pro pruned)
│   │   ├── README.md
│   │   ├── governance-auditor.md
│   │   ├── lead-software-engineer.md
│   │   ├── python-pro.md
│   │   ├── sdlc-technical-writer.md
│   │   ├── security-reviewer.md
│   │   ├── test-automator.md
│   │   └── ux-delight-specialist.md
│   ├── commands/                       # 16 /gov.* slash commands
│   │   ├── gov.audit.md
│   │   ├── gov.check-traceability.md
│   │   ├── gov.commit.md
│   │   ├── gov.implement.md
│   │   ├── gov.plan.md
│   │   ├── gov.prime.md
│   │   ├── gov.pull-request.md
│   │   ├── gov.review.md
│   │   ├── gov.session-log.md
│   │   ├── gov.spec-bump.md
│   │   ├── gov.start.md
│   │   ├── gov.status.md
│   │   ├── gov.sync.md
│   │   ├── gov.test.md
│   │   ├── gov.threat-model.md
│   │   └── gov.verify.md
│   ├── hooks/                          # runtime enforcement
│   │   ├── README.md
│   │   ├── package.json
│   │   ├── post-tool-use.cjs
│   │   ├── pre-tool-use.js
│   │   ├── session-start.cjs
│   │   └── user-prompt-submit.cjs
│   ├── skills/                         # progressive-disclosure capabilities
│   │   ├── README.md
│   │   ├── audit-trail-tail.md
│   │   ├── run-validate.md
│   │   └── traceability-update.md
│   └── settings.json                   # hook registration
├── .devcontainer/
│   ├── devcontainer.json
│   └── post-create.sh
├── .github/
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── dependabot.yml
│   └── workflows/                      # docs.yml pruned (docs site off)
│       ├── ci.yml
│       ├── release-please.yml
│       ├── release.yml
│       ├── scorecards.yml
│       └── supply-chain.yml
├── docs/
│   ├── MCP_POLICY.md
│   ├── STANDARDS.md
│   └── THREAT_MODEL.md
├── scripts/
│   ├── check-doc-drift.sh
│   ├── check-governance.sh
│   ├── check-traceability.sh
│   ├── generate-sbom.sh
│   ├── governance_review/              # GOV-NNN validator package
│   │   ├── README.md
│   │   ├── governance_review/
│   │   │   ├── __init__.py
│   │   │   ├── __main__.py
│   │   │   ├── checks.py
│   │   │   ├── cli.py
│   │   │   ├── finding.py
│   │   │   ├── formatters.py
│   │   │   └── registry.py
│   │   └── pyproject.toml
│   ├── lib/
│   │   ├── common.sh
│   │   └── governance.py
│   ├── marker-scan.sh
│   └── query-governance.sh
├── specs/
│   └── deep_specs/
│       ├── ADR/
│       │   ├── 0001-adr-template.md
│       │   └── 0002-initial-scaffold-architecture.md
│       └── README.md
└── tests/
    ├── README.md
    ├── fixtures/                       # 7 hook fixtures
    │   ├── broad-push-all.json
    │   ├── broad-push-mirror.json
    │   ├── chained-subcommand.json
    │   ├── feature-push-allowed.json
    │   ├── nested-shell.json
    │   ├── non-bash-tool.json
    │   └── protected-push.json
    ├── hook_test_spec.json
    ├── test_audit_hooks.cjs            # cross-language audit-hook contract
    ├── test_audit_hooks.py
    ├── test_command_contracts.py
    ├── test_governance_review.py
    ├── test_pre_tool_use_hook.py
    └── test_skill_contracts.py
```

### Canonical `make validate` output (Python, Day 1)

After `git init && git add -A && git commit -qm "scaffold"`:

```text
$ make validate
$ # governance-review (Phase C2 validator)
WARN   GOV-002  specs/security-requirements
          optional directory not yet present: specs/security-requirements
          see gov-002-required-files (docs/STANDARDS.md)
WARN   GOV-002  report
          optional directory not yet present: report
          see gov-002-required-files (docs/STANDARDS.md)
WARN   GOV-012  docs/STANDARDS.md:181
          referenced path does not exist: SKILL.md
          see gov-012-doc-drift (docs/STANDARDS.md)
... (10 warnings total — all GOV-002 placeholders or GOV-012 forward references)
governance-review WARN — 0 error(s), 10 warning(s)

$ # marker-scan (CRIT-001)
✓  marker-scan (6 surface(s) scanned)

$ # governance-check (CRIT-002, legacy bash)
WARN: optional directory not yet present: specs/security-requirements
WARN: optional directory not yet present: report
governance-check OK (2 warning(s))

$ # check-traceability — Phase 8 file does not exist yet
check-traceability: specs/traceability.json not present (added in Phase 8)

$ # hooks-test (CRIT-008)
Ran 18 tests in 1.356s — OK   # tests/test_pre_tool_use_hook.py
Ran  7 tests in 0.434s — OK   # tests/test_audit_hooks.py

$ # lint / typecheck / test (Python path)
lint: complete
typecheck: complete
test: complete

validate: all gates passed
```

The Day-1 baseline is **0 errors, 10 warnings**. Every warning
points at a directory or path that the project will populate in
later work — `specs/traceability.json`, `specs/security-requirements/`,
and `report/` are ledger surfaces that fill up as features land.

---

## Day 1 — TypeScript project

### Render command (TypeScript)

```sh
pipx run cookiecutter gh:Org-EthereaLogic/agentic-starter-kit \
  --no-input \
  -o "$TMPDIR/agentic-starter-kit-smoke-ts" \
  primary_language=typescript
```

### What the post-generation hook prunes

```text
Pruning unselected files…
  removed pyproject.toml
  removed tests/test_pre_tool_use_hook.py
  removed tests/test_governance_review.py
  removed .claude/agents/python-pro.md
  removed mkdocs.yml
  removed docs/index.md
  removed .github/workflows/docs.yml
  removed .copier-answers.yml
```

### File-inventory delta vs the Python vignette

The TypeScript path swaps four files and leaves the count unchanged
at 118.

```text
- .claude/agents/python-pro.md
+ .claude/agents/typescript-pro.md
- pyproject.toml
+ package.json
- tests/test_governance_review.py
- tests/test_pre_tool_use_hook.py
+ tests/test_pre_tool_use_hook.js
+ tsconfig.json
```

Everything else — the eight Makefile fragments, all 16 `/gov.*`
commands, the runtime hook tree, the seven hook fixtures, the
`scripts/governance_review/` validator package — is identical.
Layer 1 / 2 / 3 governance files are language-agnostic by design.

### Canonical `make validate` output (TypeScript, Day 1)

The TypeScript scaffold lands at the same baseline:

```text
$ make validate
... governance-review WARN — 0 error(s), 10 warning(s)
✓  marker-scan (6 surface(s) scanned)
governance-check OK (2 warning(s))
check-traceability: specs/traceability.json not present (added in Phase 8)

# hooks-test (Node)
✔ fixture: broad-push-all.json blocks                    (74.8ms)
✔ fixture: broad-push-mirror.json blocks                 (75.4ms)
✔ fixture: chained-subcommand.json blocks                (76.4ms)
✔ fixture: feature-push-allowed.json allows              (75.4ms)
✔ fixture: nested-shell.json blocks via nested shell     (76.4ms)
✔ fixture: non-bash-tool.json passes through             (76.4ms)
✔ fixture: protected-push.json blocks                    (76.4ms)
ℹ tests 18  ℹ pass 18  ℹ fail 0

lint: complete
typecheck: complete
test: complete

validate: all gates passed
```

Same governance signals, different test runner. The TypeScript path
runs `node --test tests/test_pre_tool_use_hook.js` while the Python
path runs `python3 -m unittest tests.test_pre_tool_use_hook` —
`hooks.mk` selects automatically based on which test file is
present, so polyglot scaffolds run both.

---

## Day 7 — mature project

A polyglot scaffold with the full integration set turned on, after
roughly a week of normal use. This vignette is illustrative: it
shows how the same governance surfaces evolve as a team writes
specs, lands features, and accumulates evidence.

### Render command (polyglot Day 7)

```sh
pipx run cookiecutter gh:Org-EthereaLogic/agentic-starter-kit \
  --no-input \
  -o "$TMPDIR/agentic-starter-kit-smoke-poly" \
  project_name="Acme Agentic Platform" \
  primary_language=polyglot \
  include_macaron=yes \
  include_docs_site=yes
```

The polyglot Day-1 inventory is **125 files** — the Python set plus
the TypeScript set plus the docs-site additions:

```text
+ .claude/agents/typescript-pro.md
+ .github/workflows/docs.yml
+ docs/index.md
+ mkdocs.yml
+ package.json
+ tests/test_pre_tool_use_hook.js
+ tsconfig.json
```

`include_macaron=yes` does not add a top-level file — it flips a
job inside `.github/workflows/supply-chain.yml`. The footprint
delta lives inside an existing workflow.

### What grows by Day 7

Working on the project for a week typically populates four
ledger surfaces that ship empty (or with only a template) at
render:

| Surface | Day 1 | Day 7 |
| --- | --- | --- |
| `specs/deep_specs/ADR/` | 1 template + 1 seed ADR | 4–6 ADRs (one per architecturally significant decision) |
| `specs/security-requirements/` | absent | seeded with `README.md` + 1–3 `sec-req-*.md` files |
| `specs/traceability.json` | absent | present, with one entry per accepted feature |
| `report/` | absent | append-only run logs from `make validate`, traceability checks, and threat-model updates |

A representative Day-7 tree adds, for example:

```text
specs/
├── deep_specs/
│   ├── ADR/
│   │   ├── 0001-adr-template.md           # unchanged
│   │   ├── 0002-initial-scaffold-architecture.md
│   │   ├── 0003-mcp-policy-baseline.md     # NEW — captures decision in commit 1f2a3
│   │   ├── 0004-typescript-toolchain.md    # NEW — biome over eslint
│   │   └── 0005-supply-chain-thresholds.md # NEW — Macaron severity gate
│   └── README.md
├── security-requirements/
│   ├── README.md                          # NEW — STRIDE-mapped index
│   └── sec-req-mcp-egress.md              # NEW — first scoped requirement
└── traceability.json                      # NEW — Phase 8 matrix (validated by check-traceability.sh)

report/
├── 2026-05-02T1410Z-validate-pass.md      # first green run after Phase A landed
├── 2026-05-04T0930Z-traceability-pass.md
└── 2026-05-06T1815Z-threat-model-update.md

sbom/
├── cyclonedx-python.json                  # generated by `make sbom`
└── cyclonedx-node.json
```

### Canonical `make validate` output (Day 7)

The same gates run; the output collapses to clean as the warning
sources get filled in:

```text
$ make validate
governance-review OK — 0 error(s), 0 warning(s)
✓  marker-scan (6 surface(s) scanned)
governance-check OK (0 warning(s))
check-traceability: 14 acceptance criteria mapped, 0 orphaned
check-doc-drift: 0 broken references across 18 docs
hooks-test: 18 + 7 + 18 = 43 tests passing
lint: complete
typecheck: complete
test: 89 passed in 4.2s
coverage: 87% (codecov upload threshold met)

validate: all gates passed
```

Three transitions tell the Day-1 → Day-7 story:

1. **`governance-review` 10 warnings → 0.** Each Day-1 warning
   pointed at a forward reference (`specs/traceability.json`,
   `report/`, `specs/security-requirements/`) or a STANDARDS.md
   anchor that gets defined in Phase 4 docs. Once those surfaces
   exist, the warnings drop.
2. **`check-traceability` "not present" → "14 mapped, 0 orphaned".**
   The Phase 8 traceability matrix becomes load-bearing once
   features start landing — every accepted criterion lists the
   source globs, test globs, and evidence artifact that prove it.
3. **`coverage` appears.** Day-1 has no test surface beyond the
   hook regression suite; Day-7 has feature tests measured by
   `pytest --cov` + `vitest --coverage` and uploaded by
   `codecov.yaml`'s CI job.

The runtime-hook regression (`hooks-test`) does **not** grow or
shrink between Day 1 and Day 7 — it ships locked at 18 fixtures
per language plus 7 audit-hook tests, and any new bypass class
must add a test fixture before the bypass is fixed (a CRIT-008
sub-rule documented in `.claude/hooks/README.md`).

---

## Reproducing the vignettes locally

Both Day-1 vignettes are smoke-runnable from a clone of this repo:

```sh
# Python defaults
pipx run cookiecutter . --no-input \
  -o "$TMPDIR/agentic-starter-kit-smoke-py"

# TypeScript path
pipx run cookiecutter . --no-input \
  -o "$TMPDIR/agentic-starter-kit-smoke-ts" \
  primary_language=typescript

# Polyglot + docs site + Macaron (Day-7 starting point)
pipx run cookiecutter . --no-input \
  -o "$TMPDIR/agentic-starter-kit-smoke-poly" \
  project_name="Acme Agentic Platform" \
  primary_language=polyglot \
  include_macaron=yes \
  include_docs_site=yes
```

Then, inside the rendered tree:

```sh
git init -q && git add -A
git -c user.email=smoke@example.com -c user.name=smoke commit -qm "scaffold"
make validate
make hooks-test
```

If any check exits non-zero on a freshly rendered tree, that is a
template bug — file an issue against this repository, not the
generated project.

## See also

- [`docs/BUILD_PLAN.md`](./BUILD_PLAN.md) — the phased build that
  produces the Day-1 inventory.
- [`docs/UPDATING.md`](./UPDATING.md) — how a Day-7 project absorbs
  later template releases via `copier update`.
- [`{{cookiecutter.project_slug}}/QUICKSTART.md`](../{{cookiecutter.project_slug}}/QUICKSTART.md)
  — the in-project quickstart that ships into every render.
