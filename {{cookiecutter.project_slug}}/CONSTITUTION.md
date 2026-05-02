# Constitution — {{ cookiecutter.project_name }}

> **Authority.** This document declares foundational principles and
> decision precedence for {{ cookiecutter.project_name }}. When this
> document conflicts with `DIRECTIVES.md`, `SECURITY.md`, or any
> spec, the order in §3 below resolves the conflict.
>
> **Amendment.** Decision-content changes to this document require
> an ADR under `specs/deep_specs/`. Editorial changes (typos,
> reordering for readability) do not.

---

## 1. Purpose

The Constitution declares the project's **decision-making contract**.
It states the principles that govern every change, the precedence
order that resolves disagreements between authority sources, and the
amendment process that lets the contract evolve.

The Constitution does not describe specific rules; that is the job
of `DIRECTIVES.md`. It does not describe security policy; that is
the job of `SECURITY.md`. It does not describe architecture; that
is the job of `docs/ARCHITECTURE.md`. It declares the principles
those documents derive from.

## 2. Foundational principles

The eight principles below are listed in **decision-precedence
order**. When two principles disagree, the lower-numbered one wins.

### P1 — Reality over Plausibility

Verified facts beat plausible narratives. Tool-call evidence beats
agent assertions.

- "I ran the test" is not evidence. The test runner's output is.
- "The deployment succeeded" is not evidence. The deployment log
  showing exit code zero is.
- "The library supports this method" is not evidence. The library's
  documentation or source is.

When P1 and any other principle conflict, P1 wins. Producing a
verified fact occasionally requires a small helper that violates
P6 (smallest sufficient change); P1 still wins.

### P2 — Evidence Traceability

Every claim of completion is traceable to a measured artifact under
`report/`. The audit trail is the asset.

- A commit message that says "tests pass" with no traceable
  evidence is a P1 violation by omission.
- A commit message that says "tests pass — see
  `report/2026-05-01-test-results.md`" is compliant.
- The artifact must be reachable by path, not by recollection.

### P3 — Hard Policy Boundaries

Some rules cannot be overridden by context, urgency, or instruction.
Those are the **Critical directives** (CRIT-NNN) in `DIRECTIVES.md`.

- An agent under deadline pressure is *more* bound by Critical
  directives, not less. Deadlines do not relax CRIT-NNN.
- An operator instruction that conflicts with a Critical directive
  is rejected. The operator may amend the directive (with ADR) but
  cannot bypass it for a single change.

### P4 — Explicit Failure

Errors propagate; they do not get silently swallowed.

- A bare `try / except` (or `try / catch`) that returns an empty
  list when an API call fails is a P4 violation.
- A loud failure is preferable to a quiet wrong answer.
- When error handling is added, the handler must do something
  observable: log, raise, return a tagged error, surface to user.
  "Pass" is the failure mode, not the fix.

### P5 — Append-Only Evidence

Once an evidence artifact lands in `report/`, it is not edited or
deleted. Corrections are *new* artifacts.

- Mutating the audit trail destroys forensic value.
- A retraction is a new file naming the prior file and the reason
  for retraction.
- `IMP-001` operationalizes this principle at the filesystem level.

### P6 — Smallest Sufficient Change

Speculative abstractions and premature generalization are quality
regressions, not virtues.

- A bug fix does not need surrounding cleanup.
- A one-shot operation does not need a helper function.
- Three similar lines is preferable to a premature abstraction. Wait
  for the third or fourth real use before abstracting.
- No half-finished implementations: leave the codebase functional
  at every commit.

### P7 — First-Party Boundaries

Runtime dependencies on sibling-project internals are forbidden.
Cross-project references go through published APIs only.

- The boundary between two systems is a *contract*, not a courtesy.
- Importing from a sibling project's `internal/` module makes the
  sibling's refactor your problem.
- This applies to monorepos as well: package boundaries are real
  even when the filesystem makes them blurry.

### P8 — Risk-Class Autonomy

The agent's level of autonomy is a function of the task's risk
class.

| Risk class | Trigger | Autonomy mode |
|---|---|---|
| Low | Docs, tests, refactors with green CI | YOLO (no confirmation) |
| Medium | Production-path code, schema changes | Auto (review checkpoint) |
| High | Security policies, runtime hook, release engineering | Ask (operator confirms each step) |

Demotion from YOLO to Auto, or from Auto to Ask, can be triggered
by:

- A changed file path matches a high-risk pattern (`.claude/hooks/`,
  `SECURITY.md`, `CONSTITUTION.md`, `DIRECTIVES.md`,
  `docs/THREAT_MODEL.md`).
- A change introduces new attack surface (per `/threat-model`).
- A previous step in the current session produced an unexpected
  failure or an unverifiable claim.

Promotion (relaxing autonomy) is never automatic; the operator must
explicitly elevate.

## 3. Decision order

When authority sources conflict, this order resolves the conflict.
Lower-numbered tiers win.

| Tier | Authority | Scope |
|---|---|---|
| 1 | `SECURITY.md` | Security-relevant decisions |
| 2 | `CONSTITUTION.md` | Foundational principles (this document) |
| 3 | `DIRECTIVES.md` | Specific rules (Critical / Important / Recommended) |
| 4 | `specs/deep_specs/*.md` | Canonical specs (ADRs, RFCs, designs) |
| 5 | `specs/<type>-<slug>.md` | In-flight plans not yet promoted |
| 6 | Module READMEs and code comments | Local guidance |

The order is operational, not aspirational. When `DIRECTIVES.md`
says one thing and a deep spec says another, `DIRECTIVES.md` wins —
unless `SECURITY.md` says something different, in which case
`SECURITY.md` wins everything.

## 4. Authority of agentic actors

Agents operating on this repository are bound by the same precedence
order. An agent's instructions are tier-6 authority and are
overridden by every higher tier. An agent told by an operator to
"just push to main" is bound by the Critical directive prohibiting
that action, regardless of the operator's intent.

Operators can override agents but cannot override Critical
directives without amending them through the documented amendment
process.

## 5. Amendment process

Decision-content changes to this document require:

1. An ADR under `specs/deep_specs/` documenting the change, its
   rationale, and the principles or precedence order affected.
2. A `/spec-bump` invocation per `IMP-005` if a numbered principle
   is renumbered or removed.
3. A traceability-matrix update if the changed principle is
   referenced in `specs/traceability.json`.
4. Review by the `lead-software-engineer` agent or human equivalent.

Editorial changes (typos, reordering for readability, link
corrections) do not require an ADR. They still go through the
standard PR workflow with conventional-commit prefixes.

## 6. Cross-references

- `DIRECTIVES.md` codifies the rules derived from these principles.
- `SECURITY.md` declares the security disclosure process and
  agentic-specific scope.
- `docs/ARCHITECTURE.md` documents the architecture that implements
  these principles.
- `docs/THREAT_MODEL.md` documents the threats this project's
  security posture defends against.
- `docs/STANDARDS.md` lists the external standards this constitution
  derives authority from (SWEBOK v4, ISO/IEC/IEEE 32675:2022, IEEE
  42010, AGENTS.md, IEEE 2675, CycloneDX/SPDX, CERT Top 10).

---

*Adopted on first commit. Amended via ADR per §5.*
