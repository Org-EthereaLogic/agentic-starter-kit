---
description: Review changes against the canonical spec set and validation gates
argument-hint: "<spec ID, PR number, or scope>"
allowed-tools: Read, Glob, Grep, Bash
---

# gov.review

Review {{ cookiecutter.project_name }} changes against the canonical
spec set and validation gates.

## Variables

spec_or_scope: $ARGUMENTS

## Required Pre-Read

- `CLAUDE.md`
- `AGENTS.md`
- `CONSTITUTION.md`
- `DIRECTIVES.md`
- `SECURITY.md`
- The relevant documents under `specs/deep_specs/` for the scope.
- `specs/traceability.json` for the affected acceptance criteria.

## Instructions

1. Review changed files against requirements (`docs/PRD.md`),
   architecture (`docs/ARCHITECTURE.md`), test-plan expectations,
   and traceability obligations (`specs/traceability.json`).
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
5. Run `make validate` and record per-gate outcome.
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
    "marker_scan": "pass|fail",
    "governance_check": "pass|fail",
    "check_traceability": "pass|fail",
    "check_doc_drift": "pass|fail",
    "hooks_test": "pass|fail",
    "lint": "pass|fail",
    "typecheck": "pass|fail",
    "test": "pass|fail"
  }
}
```
