---
description: Validate the traceability matrix against current source/test layout
allowed-tools: Bash, Read
---

# gov.check-traceability

Runs `make check-traceability`. Wraps `scripts/check-traceability.sh`
for ad-hoc invocation outside CI.

## Workflow

1. `make check-traceability`.
2. If clean: report PASS with the count of mapped acceptance
   criteria.
3. If dirty: surface every finding with the criterion ID, the
   missing/orphaned artifact, and the suggested remediation
   (which `/gov.implement` will need to perform).

## Report

Pass/fail. On fail: a table with columns

| Criterion ID | Issue | Suggested fix |
