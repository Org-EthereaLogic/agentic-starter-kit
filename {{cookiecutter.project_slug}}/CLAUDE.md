# CLAUDE.md — Quick reference for Claude Code in {{ cookiecutter.project_name }}

> Claude Code reads this file at session start. It is a quick
> reference — the operational spec is `AGENTS.md`. Read both before
> any substantive change.

---

## Pre-read order

Read in this order before acting. Lower-numbered tiers win when
they conflict.

1. `SECURITY.md` — tier 1 authority on security-relevant decisions.
2. `CONSTITUTION.md` — eight foundational principles in precedence
   order; six-tier decision order in §3.
3. `DIRECTIVES.md` — eighteen directives (`CRIT-NNN`, `IMP-NNN`,
   `REC-NNN`); each carries an enforcement mechanism.
4. `AGENTS.md` — operational guardrails, Plan/Act/Verify/Report
   loop, communication style, required-checks list.
5. The relevant canonical spec under `specs/deep_specs/`.
6. The `README.md` in the directory you are about to modify, when
   one exists.
7. `docs/MCP_POLICY.md` — required reading before changing
  `.mcp.json`.

## Risk-class autonomy

`CONSTITUTION.md §P8` makes autonomy a function of risk class.

| Risk class | Trigger | Autonomy mode |
| --- | --- | --- |
| Low | Docs, tests, refactors with green CI | YOLO |
| Medium | Production-path code, schema changes | Auto |
| High | Security policies, runtime hook, release engineering | Ask |

**Demotion triggers** (move toward `Ask`):

- Changed file matches a high-risk pattern: `.claude/hooks/`,
  `SECURITY.md`, `CONSTITUTION.md`, `DIRECTIVES.md`,
  `docs/THREAT_MODEL.md`.
- Change introduces new attack surface (run the threat-model
  workflow when that command is scaffolded).
- Previous step in this session produced an unexpected failure or
  an unverifiable claim.

Promotion is never automatic; the operator explicitly elevates.

## Hard rules (CRIT directives)

The eight Critical directives are hard boundaries. They cannot be
overridden by deadlines, operator instructions, or context. See
`DIRECTIVES.md` for the full statement, rationale, and enforcement
of each.

- `CRIT-001` — No forbidden stub markers in canonical surfaces.
  `DIRECTIVES.md` lists the marker strings and the surface scope.
- `CRIT-002` — Required governance files exist on every commit.
- `CRIT-003` — No runtime dependency on sibling-project internals.
- `CRIT-004` — Specs in `specs/deep_specs/` are canonical.
- `CRIT-005` — PASS claims require dual evidence.
- `CRIT-006` — No simulated data when real data is available.
- `CRIT-007` — No `--no-verify` on commits.
- `CRIT-008` — Protected-branch hook is registered and tested.

## Standard workflow — Plan / Act / Verify / Report

Detailed in `AGENTS.md`. Compressed:

- **Plan.** Read pre-read; identify scope, contract, acceptance
  criteria; name directive IDs in play.
- **Act.** Smallest sufficient change (`P6`); explicit failure
  (`P4`); explicit staging (`IMP-004`).
- **Verify.** Run the validation gate; map each acceptance
  criterion to evidence under `report/`; mark unverifiable claims
  `unverified` (`CRIT-005`).
- **Report.** Changed files, outcome, evidence paths; measured
  facts vs. interpretation; residual risks called out.

## Slash commands and agents

| Path | Purpose |
| --- | --- |
| `.claude/commands/` | Slash-command definitions. Each is a Markdown file with YAML frontmatter declaring `description`, `argument-hint`, and `allowed-tools`. |
| `.claude/agents/` | Curated subagent definitions with frontmatter declaring `name`, `description`, `model`, `memory`. |
| `.claude/skills/` | Progressive-disclosure capability packs. Single Markdown files with frontmatter declaring `name`, `description`, and a `paths:` glob list that gates lazy loading. |
| `.claude/hooks/pre-tool-use.js` | Layer 4 runtime hook. Blocks forbidden Bash patterns (`CRIT-008`). |
| `.claude/settings.json` | Hook registration. Registers `pre-tool-use.js` on `PreToolUse:Bash`. |
| `.mcp.json` | MCP server registration for this project. Ships a read-only filesystem/git baseline plus a token-scoped GitHub entry; see `docs/MCP_POLICY.md` before changing any entry. |

These `.claude/...` paths ship with every fresh scaffold. Add new
commands, agents, or skills under their respective directories and
they are picked up automatically.

## Required checks before commit

```sh
make marker-scan        # CRIT-001 — no stubs in canonical surfaces
make governance-check   # CRIT-002 — required files/folders exist
make check-traceability # specs reference real source/tests/evidence
make hooks-test         # CRIT-008 — hook regression suite green
make validate           # aggregates the above + lint/typecheck/test
```

## File map

| Path | Purpose |
| --- | --- |
| `CONSTITUTION.md`, `DIRECTIVES.md`, `SECURITY.md` | Layer 2 — constitutional foundation |
| `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` | Layer 1 — navigation |
| `.claude/` | Layer 3 — agent specialization (commands, agents, hooks) and Layer 4 — runtime enforcement (hooks, settings) |
| `Makefile`, `scripts/`, `.github/workflows/` | Layer 5 — external validation |
| `docs/` | SWEBOK-anchored documentation (architecture, operations, security program, threat model, monitoring, …) |
| `specs/deep_specs/` | Canonical specs (ADRs, RFCs, designs) |
| `specs/security-requirements/` | Per-feature security requirements |
| `specs/traceability.json` | Machine-readable traceability matrix |
| `report/` | Append-only evidence artifacts (`IMP-001`, `P5`) |
| `tests/` | Test suite, including the runtime-hook regression |

## See also

- `AGENTS.md` — full operational guardrails (this file is the
  short version).
- `GEMINI.md` — Gemini CLI quick reference (parallel to this
  file).
- `docs/STANDARDS.md` — standards register (SWEBOK v4, ISO/IEC/IEEE
  32675:2022, IEEE 42010, AGENTS.md format, IEEE 2675,
  CycloneDX/SPDX, CERT Top 10).

---

*Quick reference; the operational source of truth is `AGENTS.md`.*
