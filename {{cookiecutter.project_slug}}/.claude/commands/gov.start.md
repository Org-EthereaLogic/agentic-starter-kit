---
description: Set up the local development environment and verify the project is functional
allowed-tools: Bash, Read
---

# gov.start

Set up the local development environment and verify the project is
functional.

## Steps

1. Install dependencies: `make sync`
   (resolves to `uv sync` for the Python path, `npm install` for the
   TypeScript path, or both for polyglot, per `Makefile.fragments/sync.mk`).
2. Run the full validation suite: `make validate`
   (expands to `marker-scan`, `governance-check`,
   `check-traceability`, `check-doc-drift`, `hooks-test`, `lint`,
   `typecheck`, `test`).

## Report

Return the results of each step. Flag any failures with the specific
command, error output, and recommended corrective action before
proceeding with work. Do not claim `pass` unless every gate returned
exit code `0` (`CRIT-005`).
