---
description: Validate the traceability matrix against current source/test layout
allowed-tools: Bash, Read
---

# check-traceability

Runs `make check-traceability`. Wraps `scripts/check-traceability.sh`
for ad-hoc invocation outside CI.

## Workflow

1. If `specs/traceability.json` is absent, stop and report
   `NOT SCAFFOLDED` with the note that the matrix lands in a later
   phase and must exist before a PASS/FAIL verdict is meaningful.
2. `make check-traceability`.
3. If clean: report PASS with the count of mapped acceptance
   criteria.
4. If dirty: surface every validator finding exactly as emitted
   (missing source globs, tests globs, evidence files, or schema
   errors). Do not claim orphaned-file or orphaned-criteria
   detection that the current validator does not implement.

## Report

Pass/fail/not scaffolded. On fail: a table with columns

| Criterion ID | Issue | Suggested fix |
