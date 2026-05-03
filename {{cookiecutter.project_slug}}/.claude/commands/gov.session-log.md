---
description: Write an append-only session summary under report/
argument-hint: "[optional session topic]"
allowed-tools: Read, Write, Bash
---

# gov.session-log

Write a timestamped session recap to `report/` capturing what this
session changed, what was measured, and what remains open.
Append-only per `IMP-001`.

## Variables

topic: $ARGUMENTS

## Context snapshot

- Branch: !`git branch --show-current`
- Session commits: !`git log origin/{{ cookiecutter.default_branch_name }}..HEAD --oneline 2>/dev/null || echo "no upstream"`
- Session diff stat: !`git diff origin/{{ cookiecutter.default_branch_name }}...HEAD --stat 2>/dev/null || git diff --stat`
- Status: !`git status --short`

## Instructions

1. Write the record to
   `report/YYYY-MM-DDTHH-MM-SS-session-log.md`. Never overwrite an
   existing record (`IMP-001`).
2. Contents:
   - Session topic (`topic` or inferred from branch / commits).
   - Files touched — from the diff stat, classified as code,
     specs, docs, commands, agents, hooks, tests, evidence.
   - Commits landed this session, with hash and subject.
   - Validation results, if `make validate` or individual gates
     were run. Use `collected` vs `passed+skipped` labels.
   - Acceptance-criteria status for the session goal, if applicable.
   - Open questions / next actions — explicit, not implied.
   - Evidence links created this session (`report/...`).
3. Classify every external claim as `repo-verified`,
   `operator-reported`, or `inconclusive`.

## Rules

- No editorial commentary.
- No re-characterization of prior sync or audit records — cite them
  if relevant.
- Unsupported completeness claims are `unverified`, not `passed`
  (`CRIT-005`).

## Report

Return only the path to the created session-log record.
