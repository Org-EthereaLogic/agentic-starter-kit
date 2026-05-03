---
description: Full governance, quality-control integration, and canonical-docs audit
argument-hint: "[optional scope — e.g., governance, docs, tests]"
allowed-tools: Read, Glob, Grep, Bash, Write
---

# gov.audit

Full governance, quality-control integration, and canonical docs
audit for {{ cookiecutter.project_name }}.

## Variables

scope: $ARGUMENTS

## Context snapshot

- Branch: !`git branch --show-current`
- Recent log: !`git log --oneline -10`

## Phase 1: Required Pre-Read

- `SECURITY.md`
- `CONSTITUTION.md`
- `DIRECTIVES.md`
- `AGENTS.md`
- `CLAUDE.md`
- `README.md`
- `specs/deep_specs/README.md`
- If present and in scope: `docs/ARCHITECTURE.md`
- If present: `specs/traceability.json`

If `scope` is provided, narrow the audit accordingly; otherwise
audit the full surface.

## Phase 2: Governance compliance

- Run `make marker-scan` and record the raw hit count and file
  locations. Do not classify hits as benign — the scan is a literal
  case-insensitive grep for the forbidden stub tokens, and any hit
  in canonical surfaces is a finding regardless of surrounding
  prose (`CRIT-001`).
- Run `make governance-check` — required files and folders must be
  present (`CRIT-002`).
- Run `make lint`.
- Confirm `docs/` does not override `specs/` on any canonical claim
  (`CRIT-004`).
- Confirm quality-control integration is internally consistent for
  the files that are present in the rendered project:
  `.github/workflows/ci.yml`, `.codacy.yml`, `codecov.yaml`,
  `.snyk`, `scripts/generate-sbom.sh`, and any Macaron workflow.
  If an optional integration file is absent, classify it as
  `not scaffolded` unless another checked-in file explicitly
  requires it.

## Phase 3: Product boundary verification

- Confirm no runtime dependency on sibling project clones
  (`CRIT-003`).
- Confirm the source tree follows the taxonomy documented in
  `README.md`, `specs/deep_specs/README.md`, and the relevant ADRs.
  If `docs/ARCHITECTURE.md` exists, treat it as the stronger
  architecture index for this check.
- Verify `specs/deep_specs/` is current relative to the source
  tree (rename, deletion, or new module added without spec update
  is a finding).

## Phase 4: Test coverage

- Run `make validate` (expands to `marker-scan`,
  `governance-check`, `check-traceability`, `check-doc-drift`,
  `hooks-test`, `lint`, `typecheck`, `test`).
- When recording test totals, enumerate distinct test IDs where
  possible and label counts as `collected` vs `passed+skipped`
  explicitly.
- Treat coverage as `unverified` unless `make coverage` was run
  explicitly.

## Phase 5: Sync and traceability recency

1. **Sync recency** — most recent
    `report/*-sync-post-merge.md` is no older than the most recent
    merge to `{{ cookiecutter.default_branch_name }}`. If staler,
    surface the gap and recommend running `/gov.sync`.

2. **Traceability validity** — if `specs/traceability.json` is
  absent, report `not scaffolded` rather than PASS. If present,
  `make check-traceability` must be clean over the current state.
  Surface validator findings exactly as reported; do not claim
  orphan detection the current validator does not implement.

These steps make doc-drift mechanically auditable, not just
operator-discoverable.

## Phase 6: Report and evidence record

Return results as a JSON object with these fields: `audit_date`,
`branch`, `commit`, `scope`, `overall_status`, `governance`,
`product_boundary`, `testing`, `sync_recency`,
`traceability_validity`, `issues[]`.

Write the JSON audit to a new append-only record under `report/`
named `YYYY-MM-DDTHH-MM-SS-audit-record.md` (`IMP-001`). Never
overwrite or edit a prior audit record.
