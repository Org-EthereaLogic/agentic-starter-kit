---
description: Execute scoped work under the canonical SDLC contract
argument-hint: "<spec ID, plan path, or scoped task>"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# implement

Implement scoped work for {{ cookiecutter.project_name }} under the
canonical SDLC contract.

## Variables

scope: $ARGUMENTS

## Branch precondition

`git branch --show-current` must not return
`{{ cookiecutter.default_branch_name }}` or `master`. If it does,
stop and create a `feat/...`, `fix/...`, or `chore/...` branch
first. The `PreToolUse` hook in `.claude/hooks/pre-tool-use.js`
will block any commit or push to a protected branch (`CRIT-008`),
but this command should not waste cycles running validation before
discovering the branch is wrong.

## Required Pre-Read

Per `AGENTS.md` Required Pre-Read:

- `SECURITY.md`
- `CONSTITUTION.md`
- `DIRECTIVES.md`
- `AGENTS.md`
- `CLAUDE.md`
- The relevant canonical documents under `specs/deep_specs/`.
- The `README.md` in each directory being modified.
- `docs/MCP_POLICY.md` before changing `.mcp.json`.

## Workflow

1. Preserve the file taxonomy documented in `README.md`,
  `specs/deep_specs/README.md`, and the relevant ADRs. If
  `docs/ARCHITECTURE.md` exists, treat it as the stronger
  architecture index. Keep the layered structure described in
  `CONSTITUTION.md`.
2. Apply the smallest change that satisfies the scope (`P6`).
3. Update `specs/traceability.json` when it exists or when the
  change is scaffolding that matrix, and update the directory
  `README.md` files when behavior changes. If the matrix is not
  present in the current phase, report the traceability impact as
  `unscaffolded` rather than silently skipping it.
4. When the change produces countable items (tests, requirement IDs,
   source files), enumerate distinct IDs and label counts explicitly
   as `collected` vs `passed+skipped`. Do not infer counts from ID
   ranges.
5. Run `make validate` (or the applicable subset for the scope, per
   `CLAUDE.md`).
6. When the change should be persisted as evidence, write a
   timestamped record under `report/` following the `IMP-001`
   append-only rule.

## Subagent delegation

- `lead-software-engineer` — production-quality implementation under
  `src/` (or the language-appropriate source root).
- `python-pro` — typing, packaging, and language-specific Python
  concerns (Python or polyglot path only).
- `typescript-pro` — TypeScript types, build configuration, and
  ecosystem concerns (TypeScript or polyglot path only).
- `ux-delight-specialist` — UI/UX layer when an app frontend exists.
- `sdlc-technical-writer` — spec, traceability, and doc updates.
- `test-automator` — test strategy and validation evidence.
- `security-reviewer` — security-relevant change review (read-only,
  no implementation).
- `governance-auditor` — drift, traceability, and governance posture
  reviews (read-only).

## Rules

- Do not treat narrative `docs/` over canonical `specs/deep_specs/`
  (`CRIT-004`).
- Do not introduce hidden behavior, unverifiable claims, or marker
  strings prohibited by `CRIT-001`.
- Keep evidence and verification expectations explicit (`P5`).
- No runtime dependency on sibling project clones (`CRIT-003`).
- No simulated data when real data is available (`CRIT-006`).
- Hard policy boundaries (`CRIT-***`) apply in all autonomy modes,
  including YOLO (`P8`).

## Report

Return changed files, acceptance-criteria status (each AC with
evidence location), and `make validate` outcome per gate. Mark
unsupported claims as `unverified`, never as `passed` (`CRIT-005`).
