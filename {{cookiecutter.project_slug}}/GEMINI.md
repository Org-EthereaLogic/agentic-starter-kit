# GEMINI.md — Quick reference for Gemini CLI in {{ cookiecutter.project_name }}

> Gemini CLI reads this file at session start. It is the
> Gemini-CLI-specific entry point; the cross-runtime operational
> spec is `AGENTS.md` and the Claude-Code-specific entry point is
> `CLAUDE.md`. This file mirrors the structure of those two so a
> reader of any one of the three has the same operating model.

---

## Pre-read order

Read these files in order before any substantive change. Lower-
numbered tiers win when they conflict.

1. `SECURITY.md` — tier 1 authority on security-relevant decisions.
2. `CONSTITUTION.md` — eight foundational principles in precedence
   order; six-tier decision order in §3.
3. `DIRECTIVES.md` — eighteen directives (`CRIT-NNN`, `IMP-NNN`,
   `REC-NNN`).
4. `AGENTS.md` — operational guardrails, Plan/Act/Verify/Report
   loop, communication style, required checks.
5. The relevant canonical spec under `specs/deep_specs/`.
6. The `README.md` in the directory you are about to modify, when
   one exists.

## Risk-class autonomy

`CONSTITUTION.md §P8` makes autonomy a function of risk class.

| Risk class | Trigger | Autonomy mode |
|---|---|---|
| Low | Docs, tests, refactors with green CI | YOLO |
| Medium | Production-path code, schema changes | Auto |
| High | Security policies, runtime hook, release engineering | Ask |

Demote toward `Ask` when:

- Changed file matches `.claude/hooks/`, `SECURITY.md`,
  `CONSTITUTION.md`, `DIRECTIVES.md`, `docs/THREAT_MODEL.md`.
- A change introduces new attack surface.
- A previous step in this session produced an unexpected failure
  or unverifiable claim.

Promotion is never automatic; the operator explicitly elevates.

## Hard rules (Critical directives)

The eight Critical directives are hard boundaries. They cannot be
overridden by deadlines, operator instructions, or context.

- `CRIT-001` — No forbidden stub markers in canonical surfaces.
  `DIRECTIVES.md` lists the marker strings and the surface scope.
- `CRIT-002` — Required governance files exist on every commit.
- `CRIT-003` — No runtime dependency on sibling-project internals.
- `CRIT-004` — Specs in `specs/deep_specs/` are canonical.
- `CRIT-005` — PASS claims require dual evidence.
- `CRIT-006` — No simulated data when real data is available.
- `CRIT-007` — No `--no-verify` on commits.
- `CRIT-008` — Git-layer protected-branch guards are installed and
  tested; the agent-layer hook provides defense in depth.

See `DIRECTIVES.md` for full statements, rationales, and
enforcement mechanisms.

## Standard workflow — Plan / Act / Verify / Report

Compressed; full version in `AGENTS.md`.

- **Plan.** Read pre-read; identify scope, contract, acceptance
  criteria; name directive IDs in play.
- **Act.** Smallest sufficient change (`P6`); explicit failure
  (`P4`); explicit staging (`IMP-004` — never `git add -A`).
- **Verify.** Run the validation gate; map each acceptance
  criterion to evidence under `report/`; mark unverifiable claims
  `unverified` (`CRIT-005`).
- **Report.** Changed files, outcome, evidence paths; measured
  facts vs. interpretation; residual risks called out.

## Communication style

- Declarative, present-tense prose. "The hook blocks pushes to
  main" — not "the hook will block."
- No hedging language ("may", "might", "could potentially") in
  policy or directive prose.
- Cite directive IDs (`CRIT-001`) and SWEBOK chapter sections
  (`SWEBOK v4 §6.4`) when introducing a governance-anchored
  concept.
- Distinguish measured facts from interpretation.
- Mark unsupported claims `unverified`, never `passed`.
- Wrap prose at ~80 columns for diff-friendliness.

## Required checks before commit

Once the build glue is scaffolded, every substantive change passes
these locally before commit:

- `make marker-scan` — `CRIT-001`.
- `make governance-check` — `CRIT-002`.
- `make check-traceability` — traceability matrix is clean.
- `make hooks-test` — `CRIT-008`.
- `make lint`, `make typecheck`, `make test`, `make coverage`.
- `make validate` — aggregates the above.

Until that aggregate target is in place, run each check
individually or rely on reviewer attention.

## File map

| Path | Purpose |
|---|---|
| `CONSTITUTION.md`, `DIRECTIVES.md`, `SECURITY.md` | Layer 2 — constitutional foundation |
| `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` | Layer 1 — navigation (this file) |
| `.claude/` | Layer 3 — agent specialization; Layer 4 — runtime enforcement |
| `Makefile`, `scripts/`, `.github/workflows/` | Layer 5 — external validation |
| `docs/` | SWEBOK-anchored documentation |
| `specs/deep_specs/` | Canonical specs (ADRs, RFCs, designs) |
| `specs/security-requirements/` | Per-feature security requirements |
| `specs/traceability.json` | Machine-readable traceability matrix |
| `report/` | Append-only evidence artifacts (`IMP-001`, `P5`) |
| `tests/` | Test suite, including the runtime-hook regression |

## See also

- `AGENTS.md` — full operational spec, structurally consistent
  with this file.
- `CLAUDE.md` — Claude Code's quick reference, parallel to this
  file.
- Methodology essay — include separately if this scaffold adds
  one.
- `docs/STANDARDS.md` — external standards register (when
  scaffolded).

---

*Quick reference for Gemini CLI; the operational source of truth
is `AGENTS.md`.*
