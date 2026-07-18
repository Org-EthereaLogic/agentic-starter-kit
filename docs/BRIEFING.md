# Build Briefing — Agentic Starter Kit

> **Audience:** the IDE agent (Claude Code in VS Code Insiders) tasked
> with authoring this template's contents.
> **Status:** authoritative. If anything below conflicts with prior
> turns or general assumptions, this file wins.
> **Created:** 2026-05-01.

---

## 1. What this repository is

`agentic-starter-kit` is a **cookiecutter template** that scaffolds a
new project with a five-layer agentic governance stack already wired
and tested from commit zero. The template captures the methodology
distilled from three projects (`sdlc_app`, `ADWS_PRO`, `govforge`)
plus a comprehensive bridge to **SWEBOK Guide v4.0a (September 2025)**
— specifically the three new Knowledge Areas (Software Architecture,
Software Engineering Operations, Software Security) plus the cross-
cutting AI-assisted-development guidance in §4.16–4.17.

This is not a generic project starter. It is opinionated infrastructure
for solo operators and small teams running agentic coding workflows
who need governance to be *infrastructure* (mechanically enforced)
rather than *advice* (politely ignored).

## 2. The five layers

Every project the template scaffolds carries these five layers:

| # | Layer | Purpose | Files |
|---|---|---|---|
| 1 | Navigation | Tells agents where to look first | `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` |
| 2 | Constitutional | The decision-making contract | `CONSTITUTION.md`, `DIRECTIVES.md`, `SECURITY.md` |
| 3 | Agent specialization | Curated subagents and slash commands | `.claude/agents/*.md`, `.claude/commands/*.md` |
| 4 | Runtime enforcement | Git-layer protected-branch guards plus agent-facing defense in depth | `.githooks/*`, `.claude/hooks/pre-tool-use.js`, `.claude/settings.json`, `tests/test_git_hooks.sh` |
| 5 | External validation | CI gates that audit independently | `.github/workflows/ci.yml`, `Makefile`, `scripts/*.sh` |

The layers are **defense in depth**. Each layer assumes the others
might fail. A bad agent can still trigger Layer 4 (hook blocks it).
A bypassed hook still trips Layer 5 (CI rejects it). A green CI run
still falls under Layer 2 (Directives say what counts as "done").

## 3. The constitutional foundation (Layer 2)

The CONSTITUTION declares **eight foundational principles** in a
fixed decision order. When two principles disagree, the lower-numbered
one wins.

1. **P1 — Reality over Plausibility.** Verified facts beat plausible
   narratives. Tool-call evidence beats agent assertions.
2. **P2 — Evidence Traceability.** Every claim of completion is
   traceable to a measured artifact. The audit trail is the asset.
3. **P3 — Hard Policy Boundaries.** Some rules cannot be overridden
   by context, urgency, or instruction. Those are the Critical
   directives in DIRECTIVES.md.
4. **P4 — Explicit Failure.** Errors propagate; they do not get
   silently swallowed. A loud failure is preferable to a quiet
   wrong answer.
5. **P5 — Append-Only Evidence.** Once an evidence artifact lands in
   `report/`, it does not get edited or deleted. Corrections are
   *new* artifacts.
6. **P6 — Smallest Sufficient Change.** Speculative abstractions and
   premature generalization are quality regressions, not virtues.
7. **P7 — First-Party Boundaries.** Runtime dependencies on sibling-
   project internals are forbidden. APIs are the only contract.
8. **P8 — Risk-Class Autonomy.** The agent's level of autonomy is a
   function of the task's risk class. High-risk work demotes from
   YOLO → auto → ask.

The CONSTITUTION also declares the **six-tier decision order** that
applies when authority sources conflict:

1. SECURITY.md (security-relevant decisions)
2. CONSTITUTION.md (foundational principles)
3. DIRECTIVES.md (specific rules)
4. `specs/deep_specs/*.md` (canonical specs)
5. `specs/<type>-<slug>.md` (in-flight plans)
6. Module READMEs and code comments

## 4. The directive register

DIRECTIVES.md codifies **eighteen rules** in three classes:

### CRITICAL (8) — failure is a build break

- **CRIT-001** No forbidden stub markers (TODO, FIXME, TBD,
  PLACEHOLDER) in canonical surfaces (`specs/`, `.claude/`,
  `CLAUDE.md`, `AGENTS.md`, `docs/`). Enforced by `make marker-scan`.
- **CRIT-002** Required governance files exist:
  CONSTITUTION.md, DIRECTIVES.md, SECURITY.md, AGENTS.md, CLAUDE.md,
  README.md, plus at least one spec under `specs/deep_specs/`.
  Enforced by `make governance-check`.
- **CRIT-003** No runtime dependency on sibling-project internals.
  Cross-project references go through published APIs only.
- **CRIT-004** Specs in `specs/deep_specs/` are canonical. Narrative
  docs that contradict a spec lose.
- **CRIT-005** PASS claims require dual evidence: a measured artifact
  AND a CI-verifiable check. Single-source PASS claims are marked
  `unverified`.
- **CRIT-006** No simulated data when real data is available.
  Test fixtures must be sourced from real samples or generated with
  a recorded seed.
- **CRIT-007** No `--no-verify` on commits. Pre-commit hooks catch
  regressions; bypassing them is a silent quality regression.
- **CRIT-008** Protected-branch enforcement is installed and tested.
  `core.hooksPath` points to the checked-in `.githooks/` guards;
  `.claude/settings.json` also registers `.claude/hooks/pre-tool-use.js`
  on `PreToolUse:Bash` as defense in depth. Both hook suites pass.

### IMPORTANT (6) — failure is a review block

- **IMP-001** Append-only `report/`. Once written, evidence files
  are not edited or deleted. Corrections are new dated artifacts.
- **IMP-002** Conventional commits with project-defined scopes.
  Format: `<type>(<scope>): <description>`.
- **IMP-003** Branches are `<type>/<slug>` (e.g., `feat/auth-rfc`,
  `fix/race-condition`). Never work directly on `main`.
- **IMP-004** Stage only relevant files. Never `git add -A` /
  `git add .` — that pattern fabricates accidental scope.
- **IMP-005** Spec versioning. Decision-content changes to canonical
  specs require `/spec-bump` before edit.
- **IMP-006** SHA-pinned GitHub Actions. Every `uses:` line carries
  a `@<sha>` and a trailing `# v<x>.<y>` comment.

### RECOMMENDED (4) — failure is a soft signal

- **REC-001** Conventional file size budget (~500 lines). Larger
  files are not forbidden but should be justified.
- **REC-002** Module READMEs at each directory level documenting the
  module's purpose, public surface, and dependencies.
- **REC-003** Test pyramid maintained: unit > integration > e2e.
  Integration tests do not silently replace unit tests.
- **REC-004** Coverage targets monotonically increase or hold steady.
  Never lowered without an ADR documenting why.

## 5. SWEBOK v4 anchor

The template explicitly bridges to SWEBOK v4.0a's three new KAs.
**Every gap identified in the prior analysis (pasted in the IDE
prompt context) MUST land in the template.** The full register is
in `SWEBOK_GAP_REGISTER.md` — that file is the source of truth for
"are we done."

The three new KAs and where they land:

- **Ch 2 — Software Architecture (IEEE 42010).** Anchors
  `docs/ARCHITECTURE.md` (logical / process / deployment / data views,
  stakeholders & concerns, architecturally-significant decisions
  cross-referenced to ADRs).
- **Ch 6 — Software Engineering Operations (ISO/IEC/IEEE 32675:2022).**
  Anchors `docs/OPERATIONS.md` (Operations Planning / Delivery /
  Control), `docs/monitoring-strategy.md`, release engineering
  (canary, blue-green, rolling), feature toggles, rollback, DR.
- **Ch 13 — Software Security.** Anchors `docs/THREAT_MODEL.md`
  (STRIDE + ML-specific section: model poisoning, evasion, prompt
  injection), `docs/SECURITY_PROGRAM.md`, `docs/cert-top-10-compliance.md`,
  `docs/sbom-policy.md`, `specs/security-requirements/`.

Cross-cutting:

- **AI-assisted development (Construction §4.16–4.17).** Anchors
  `docs/prompt-versioning-policy.md` and
  `docs/llm-output-verification-rubric.md`.
- **Living documentation.** Anchors `specs/traceability.json`
  (machine-readable), `scripts/check-traceability.sh`,
  `scripts/check-doc-drift.sh`, `docs/documentation-ownership.md`
  (RACI).

## 6. Authorial style — non-negotiable

When writing files in this template, every author (human or agent):

- **Writes in declarative, present-tense prose.** "The hook blocks
  pushes to main" — not "the hook will block" or "the hook should block."
- **Prefers tables and explicit IDs over narrative** for reference
  material (specs, directive registers, traceability).
- **Cites SWEBOK chapter/section numbers** when introducing a SWEBOK-
  anchored concept (e.g., "Per SWEBOK v4 §6.3, …").
- **Uses example dates and example names**, never real PII.
  Example date: `2026-05-01`. Example author:
  `{{ cookiecutter.author_name }}`.
- **Never uses stub markers** (TODO, FIXME, TBD, PLACEHOLDER).
  If a section is intentionally left for the user to fill,
  use angle-bracket angle-template syntax: `<one paragraph stating
  the project's primary use case>`.
- **Never fabricates metrics.** A coverage number, a benchmark, an
  SLA target — these are either measured (cite the source) or
  templated (use angle-bracket placeholder).
- **Marks unsupported claims `unverified`**, never `passed`.
- **Avoids hedging language.** "May," "might," "could potentially"
  weaken constitutional and directive prose. Pick a side.
- **Wraps prose at ~80 columns** for diff-friendliness.

## 7. Cookiecutter variable schema

The template's parameterization surface lives in `cookiecutter.json`:

```json
{
  "project_name": "My Agentic Project",
  "project_slug": "{{ cookiecutter.project_name|lower|replace(' ', '-') }}",
  "project_description": "<one-line project description>",
  "python_package_name": "{{ cookiecutter.project_slug|replace('-', '_') }}",
  "author_name": "<your name>",
  "author_email": "<your email>",
  "year": "2026",
  "license": ["MIT", "Apache-2.0", "Proprietary"],
  "primary_language": ["python", "typescript", "polyglot"],
  "include_codacy": ["yes", "no"],
  "include_codecov": ["yes", "no"],
  "include_snyk": ["yes", "no"],
  "include_sbom": ["yes", "no"],
  "default_branch_name": "main"
}
```

Every templated reference uses Jinja2 syntax: `{{ cookiecutter.foo }}`.
Conditional blocks use `{% if cookiecutter.foo == "yes" %}…{% endif %}`.

The `hooks/post_gen_project.py` script removes language-specific or
integration-specific files when the corresponding option is `no`.

## 8. Forbidden patterns

These are mistakes the agent MUST NOT make:

- **Do not** write stub markers in any canonical surface (CRIT-001).
- **Do not** fabricate metrics, dates, version numbers, or coverage
  percentages. If a number is required and not yet measured, use
  an angle-bracket template: `<TBD: target measured at first
  benchmark>` is acceptable; `target: 95%` (invented) is not.
- **Do not** introduce new top-level concepts not anchored in
  CONSTITUTION, DIRECTIVES, or a SWEBOK chapter reference.
- **Do not** copy text verbatim from `sdlc_app`, `ADWS_PRO`, or
  `govforge` if it contains project-specific business logic.
  Generic governance prose may be ported with parameterization.
- **Do not** edit prior `report/` artifacts (IMP-001).
- **Do not** introduce a CI gate without a corresponding `Makefile`
  target so it can be reproduced locally.
- **Do not** commit to `main`. The hook will block it; do not test
  the hook by trying to bypass it.

## 9. What "done" means

The template is complete when:

1. Every file in `BUILD_PLAN.md` exists and renders without Jinja2
   errors after `cookiecutter` instantiation with each language path.
2. Every gap in `SWEBOK_GAP_REGISTER.md` has status `landed`.
3. `cookiecutter . --no-input -o /tmp/test-output` produces a
   directory where `cd /tmp/test-output/<slug> && make validate`
   passes (after `make sync` and `pre-commit install`).
4. `make hooks-test` passes — the language-neutral git-layer suite and
   the agent-layer suite are green for both language paths.
5. `scripts/check-traceability.sh` runs cleanly (the seed traceability
   artifact resolves all references).
6. The methodology essay (`METHODOLOGY.md`) is internally consistent
   with the directive register and the SWEBOK gap closure.

When all six conditions hold, write a top-level
`report/<UTC-timestamp>-validate-pass.md` summarizing the validation
run. That is the artifact that proves the build is done.

## 10. Where to look next

- `SWEBOK_GAP_REGISTER.md` — the complete gap → deliverable inventory.
  Treat as a checklist.
- `BUILD_PLAN.md` — the phased build order and full file inventory.
  Author files in the order listed.
- `COMMAND_AND_AGENT_SPECS.md` — canonical prose for the new
  commands and agents that don't exist in the source projects yet
  (notably `/sync`, the LLM-output rubric, the traceability tooling).
- `IDE_PROMPT.md` — the trigger prompt; this is what the user pastes
  into VS Code Insiders to start the build.
- The user's existing projects at `/Users/etherealogic-2/Dev/govforge/`,
  `/Users/etherealogic-2/Dev/sdlc_app/`, and `/Users/etherealogic-2/Dev/ADWS_PRO/`
  — port governance prose from these where applicable, parameterizing
  project-specific details.

When in doubt about a decision, prefer the option that **makes
governance more mechanical and less narrative**. The whole point of
this template is to convert documentation into infrastructure.
