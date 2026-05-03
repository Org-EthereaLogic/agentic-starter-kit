---
description: Run the validation suite and return structured results
argument-hint: "[optional gate — marker-scan, governance-check, check-traceability, check-doc-drift, hooks-test, lint, typecheck, test]"
allowed-tools: Bash
---

# gov.test

Run the {{ cookiecutter.project_name }} validation suite and return
structured results.

## Variables

target: $ARGUMENTS

## Instructions

- If `target` is empty or `all`, run `make validate`.
- Otherwise run the specific gate requested.
- Each Bash call should be invoked with `timeout: 300000` (5 minutes).
- Capture the result (passed/failed) and any error messages.
- If a gate fails, include the error message and stop processing
  remaining gates.
- When recording test totals, label counts as `collected` vs
  `passed+skipped` explicitly — never a bare "total tests" row.

## Gate sequence

`make validate` expands to these gates in order, per the project
`Makefile`. Stop on first failure.

| # | test_name | execution_command | test_purpose |
|---|---|---|---|
| 1 | `marker-scan` | `make marker-scan` | No forbidden stub markers in canonical surfaces (`CRIT-001`) |
| 2 | `governance-check` | `make governance-check` | Required governance files and folders exist (`CRIT-002`) |
| 3 | `check-traceability` | `make check-traceability` | `specs/traceability.json` references exist on disk |
| 4 | `check-doc-drift` | `make check-doc-drift` | Path references in `docs/` and `specs/` resolve |
| 5 | `hooks-test` | `make hooks-test` | Runtime hook regression suite green (`CRIT-008`) |
| 6 | `lint` | `make lint` | Language linter(s) clean |
| 7 | `typecheck` | `make typecheck` | Static type-checker(s) clean |
| 8 | `test` | `make test` | Unit + integration test suite green |

## Report

Return results exclusively as a JSON array. Sort failed gates first.

```json
[
  {
    "test_name": "string",
    "passed": true,
    "execution_command": "string",
    "test_purpose": "string",
    "counts": { "collected": 0, "passed": 0, "skipped": 0, "failed": 0 },
    "error": "optional string"
  }
]
```
