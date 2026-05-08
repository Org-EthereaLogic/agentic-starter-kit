---
description: Review changes against the canonical spec set and validation gates
argument-hint: "<spec ID, PR number, or scope>"
allowed-tools: Read, Glob, Grep, Bash
---

# review

Review {{ cookiecutter.project_name }} changes against the canonical
spec set and validation gates.

## Variables

spec_or_scope: $ARGUMENTS

## Required Pre-Read

- `SECURITY.md`
- `CONSTITUTION.md`
- `DIRECTIVES.md`
- `AGENTS.md`
- `CLAUDE.md`
- The relevant documents under `specs/deep_specs/` for the scope.
- The `README.md` in each directory being reviewed.
- If present: `specs/traceability.json`
- If present: `docs/ARCHITECTURE.md`

## Instructions

1. Review changed files against the relevant canonical specs under
  `specs/deep_specs/`, the project `README.md` and directory
  READMEs, the constitutional docs, and, when scaffolded, the
  supporting artifacts `docs/ARCHITECTURE.md` and
  `specs/traceability.json`.
2. Check for prohibited stub markers (`make marker-scan`),
   unverifiable claims, drift between `docs/` and `specs/`, and
   broken repository taxonomy.
3. When counts are claimed in changes (test totals, requirement
   coverage), independently enumerate distinct IDs from the source.
   Label counts as `collected` vs `passed+skipped` explicitly.
4. When hook or governance tests are added or modified, confirm the
   traceability mapping cites the correct directive
   (`CRIT-008` for hook regressions, `CRIT-002` for governance file
   presence) rather than a feature-level requirement.
5. Run the validation gates individually in `make validate` order
  and record each outcome: `make marker-scan`,
  `make governance-check`, `make check-traceability`,
  `make check-doc-drift`, `make hooks-test`, `make lint`,
  `make typecheck`, `make test`. When a gate explicitly reports a
  later-phase prerequisite is absent, record `not_scaffolded`
  instead of `pass`.
6. For security-relevant changes, delegate to the
   `security-reviewer` subagent and require its sign-off before
   recommending merge.

## Report

Return a JSON object:

```json
{
  "success": true,
  "review_summary": "...",
  "review_issues": [
    {"severity": "blocker|major|minor", "file": "...", "line": 0, "note": "..."}
  ],
  "make_validate": {
    "marker_scan": "pass|fail|not_scaffolded",
    "governance_check": "pass|fail|not_scaffolded",
    "check_traceability": "pass|fail|not_scaffolded",
    "check_doc_drift": "pass|fail|not_scaffolded",
    "hooks_test": "pass|fail|not_scaffolded",
    "lint": "pass|fail|not_scaffolded",
    "typecheck": "pass|fail|not_scaffolded",
    "test": "pass|fail|not_scaffolded"
  }
}
```
