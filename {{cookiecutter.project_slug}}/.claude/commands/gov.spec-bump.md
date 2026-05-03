---
description: Bump a canonical spec's version and append a revision-history entry
argument-hint: "<spec filename> <patch|minor|major> <reason>"
allowed-tools: Read, Edit, Glob, Grep, Bash
---

# gov.spec-bump

Bump the version of a canonical document under `specs/deep_specs/`
and add a revision-history entry. Preserves the document's
versioning contract (`CRIT-004`).

## Variables

args: $ARGUMENTS

Expected form: `<spec> <bump-kind> <reason>` — e.g.,
`adr-0001-governance-foundation.md patch drift repair after PR #168`.

## Required Pre-Read

- `CLAUDE.md`
- The target spec file under `specs/deep_specs/`.
- Any sibling specs cited in the reason (e.g., if the bump touches
  a contract, also read the design doc and any ADRs that depend on
  it for cross-consistency).

## Workflow

1. Parse `args` into `spec`, `bump_kind`, `reason`.
2. Locate the spec at `specs/deep_specs/<spec>` (glob if needed).
3. Read the current `Version` field from the document
   frontmatter-style table (e.g., `| Version | 0.36 |`).
4. Compute the new version per `bump_kind`:
   - `patch`: `0.36` → `0.37`
   - `minor`: `0.36` → `0.40` (round up the tenths for content
     additions)
   - `major`: `0.36` → `1.0` (reserved for contract-breaking
     changes)
5. Update the `Version` field.
6. Append a new row to the Revision History table:
   `| <new-version> | <YYYY-MM-DD> | <author> | <reason> |`
7. If the spec cites test counts, re-enumerate distinct IDs from
   the source and label counts as `collected` vs `passed+skipped`.
8. Run `make marker-scan` — the new revision entry must not
   introduce forbidden markers (`CRIT-001`).

## Rules

- Never edit prior revision-history entries. Append only
  (`IMP-001`).
- Never edit version numbers anywhere other than the `Version`
  field and the new revision-history row.
- If the change alters contract semantics, the bump kind must be
  `major` and the operator must confirm.

## Report

```json
{
  "spec": "specs/deep_specs/...",
  "old_version": "...",
  "new_version": "...",
  "revision_row_added": true,
  "marker_scan": "pass|fail"
}
```
