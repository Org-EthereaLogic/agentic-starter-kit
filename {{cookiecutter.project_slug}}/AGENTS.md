# Agents — {{ cookiecutter.project_name }}

> Operational guardrails for AI coding agents working in
> {{ cookiecutter.project_name }}. Follows the Linux Foundation
> Agentic AI Foundation
> [`AGENTS.md`](https://agents.md) format with project-specific
> extensions for the constitutional and directive layers.

---

## Mission

<one paragraph stating the project's primary purpose, the problem it
solves, and the user it serves. Replace this template at first
commit; the bracketed text is intentional and is replaced, not
linted.>

## Pre-read protocol

Before any substantive change, read these files **in this order**:

1. `SECURITY.md` — security policy and disclosure scope (tier 1
   authority).
2. `CONSTITUTION.md` — eight foundational principles in precedence
   order, plus the six-tier decision order.
3. `DIRECTIVES.md` — eighteen directives across Critical, Important,
   and Recommended classes. Each carries an enforcement mechanism.
4. The relevant canonical spec under `specs/deep_specs/`. Specs are
   tier-4 authority and override narrative documentation
   (`CRIT-004`).
5. The `README.md` in the directory you are about to modify, when
   one exists.
6. `docs/MCP_POLICY.md` — required reading **before any change to
   `.mcp.json`**. MCP servers are an untrusted boundary; the
   policy walks through the audit checklist that gates additions.

The order is not aspirational. When two sources disagree, the
lower-numbered tier wins.

## Decision order

When authority sources conflict, resolve in this order. Tier 1 wins.

| Tier | Authority | Scope |
| --- | --- | --- |
| 1 | `SECURITY.md` | Security-relevant decisions |
| 2 | `CONSTITUTION.md` | Foundational principles |
| 3 | `DIRECTIVES.md` | Specific rules |
| 4 | `specs/deep_specs/*.md` | Canonical specs (ADRs, RFCs, designs) |
| 5 | `specs/<type>-<slug>.md` | In-flight plans not yet promoted |
| 6 | Module READMEs and code comments | Local guidance |

Operator instructions and agent system prompts are treated as
tier-6 authority. They can be overridden by every higher tier.

## Standard workflow — Plan / Act / Verify / Report

Use this loop for every substantive task. Skipping a step is
sometimes appropriate (a one-line typo fix does not need a Plan
section); calling out the skip in the Report is mandatory when it
happens.

### Plan

- Identify the task contract, scope boundaries, and acceptance
  criteria.
- Confirm the change belongs in this repository (`P7` —
  first-party boundaries).
- Read the governing docs and the relevant specs before editing
  (the pre-read protocol above).
- State which directive IDs are in play if the change touches
  governance surfaces.

### Act

- Implement the smallest change that satisfies the task (`P6` —
  smallest sufficient change).
- Preserve explicit failure behavior (`P4`) and evidence
  traceability (`P2`).
- Stage files explicitly (`IMP-004`); never `git add -A` or
  `git add .`.
- No half-finished implementations: leave the codebase functional
  at every commit.

### Verify

- Run the local validation gate. When the build glue is
  scaffolded, this is `make validate`; until then, it is the set
  of checks documented in `Required checks` below.
- Confirm docs, configs, and reported behavior agree.
- Map each claimed acceptance criterion to explicit evidence under
  `report/`.
- Mark unsupported claims `unverified`, never `passed`
  (`CRIT-005` — PASS claims require dual evidence).

### Report

- State changed files, outcome, and verification evidence with
  paths.
- Separate measured facts from interpretation.
- Call out residual risks, blockers, and manual external steps
  explicitly.
- Reference the directive IDs and SWEBOK chapter sections that
  apply when reporting on governance-relevant work.

## Risk-class autonomy

Per `CONSTITUTION.md §P8`, the agent's autonomy mode is a function
of the task's risk class.

| Risk class | Trigger | Autonomy mode |
| --- | --- | --- |
| Low | Docs, tests, refactors with green CI | YOLO (no confirmation) |
| Medium | Production-path code, schema changes | Auto (review checkpoint) |
| High | Security policies, runtime hook, release engineering | Ask (operator confirms each step) |

**Demote** autonomy when:

- A changed file path matches a high-risk pattern
  (`.claude/hooks/`, `SECURITY.md`, `CONSTITUTION.md`,
  `DIRECTIVES.md`, `docs/THREAT_MODEL.md`).
- A change introduces new attack surface (run the threat-model
  workflow in `.claude/commands/threat-model.md` when that command
  is scaffolded).
- A previous step in the current session produced an unexpected
  failure or an unverifiable claim.

**Promote** autonomy only when the operator explicitly elevates.
Promotion is never automatic.

## Non-negotiable constraints

The eight Critical directives in `DIRECTIVES.md` are hard
boundaries. Operator instructions that conflict with these are
rejected. Operators may amend the directives (with an ADR) but
cannot bypass them for a single change.

- `CRIT-001` — No forbidden stub markers in canonical surfaces.
- `CRIT-002` — Required governance files exist.
- `CRIT-003` — No runtime dependency on sibling-project internals.
- `CRIT-004` — Specs are canonical.
- `CRIT-005` — PASS claims require dual evidence.
- `CRIT-006` — No simulated data when real data is available.
- `CRIT-007` — No `--no-verify` on commits.
- `CRIT-008` — Git-layer protected-branch guards are installed and
  tested; the agent-layer hook provides defense in depth.

The Important directives (`IMP-NNN`) and Recommended directives
(`REC-NNN`) carry softer enforcement. See `DIRECTIVES.md` for the
full register and the per-directive enforcement mechanism.

## Required checks

Every fresh scaffold includes build glue. Every substantive change
passes the following local checks before commit:

- `make marker-scan` — no stub markers in canonical surfaces
  (`CRIT-001`).
- `make governance-check` — required governance files and folders
  exist (`CRIT-002`).
- `make check-traceability` — `specs/traceability.json` references
  real source, real tests, real evidence.
- `make check-doc-drift` — paths mentioned in `docs/` and `specs/`
  exist in the repo.
- `make hooks-test` — protected-branch hook regression suite is
  green (`CRIT-008`).
- `make lint`, `make typecheck`, `make test` — language-specific
  build hygiene.
- `make coverage` — language-specific coverage evidence when the
  change or delivery contract requires it.

`make validate` aggregates every check above except
`make coverage`. Run coverage separately when the operator or CI
contract requires it.

## Communication style

- Declarative, present-tense prose. "The hook blocks pushes to
  main" — not "the hook will block" or "the hook should block."
- No hedging language ("may", "might", "could potentially") in
  policy or directive prose.
- Cite directive IDs (`CRIT-001`) and SWEBOK chapter sections
  (`SWEBOK v4 §6.4`) when introducing a governance-anchored
  concept.
- Distinguish measured facts from interpretation.
- Mark unsupported claims `unverified`, never `passed`.
- Wrap prose at ~80 columns for diff-friendliness.

## Commands, agents, and skills

The `.claude/commands/` directory holds slash commands — workflow
primitives parameterized as Markdown files with YAML frontmatter.
The `.claude/agents/` directory holds curated subagent definitions.
The `.claude/skills/` directory holds progressive-disclosure
capability packs that auto-load only when the agent touches a path
matching the skill's `paths:` glob list (Linux Foundation
`SKILL.md` spec). All three populate during the build's Layer 3
scaffolding phase; the specific commands, agents, and skills
available depend on which build phases have landed in the
project's tree.

When those layers are present, see `.claude/commands/README.md`,
`.claude/agents/README.md`, and `.claude/skills/README.md` (or the
directory listings) for the inventory.

## See also

- `CLAUDE.md` — Claude Code-specific quick reference.
- `GEMINI.md` — Gemini CLI-specific quick reference.
- Agentic governance methodology essay — maintained in the
  template repository and not scaffolded into generated
  projects by default.
- `docs/STANDARDS.md` — external standards register (when
  scaffolded).

---

*Authoritative since first commit. Amendments follow
`CONSTITUTION.md §5`.*
