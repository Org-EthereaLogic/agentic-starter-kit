---
description: Bump a canonical spec's revision surface and append a history entry
argument-hint: "<spec filename> <patch|minor|major> <reason>"
allowed-tools: Read, Edit, Glob, Grep, Bash
---

# spec-bump

Bump the version of a canonical document under `specs/deep_specs/`
and add a revision-history entry. Preserves the document's
versioning contract (`CRIT-004`).

## Variables

args: $ARGUMENTS

Expected form: `<spec> <bump-kind> <reason>` — e.g.,
`ADR/0002-initial-scaffold-architecture.md patch drift repair after PR #32`.

## Required Pre-Read

- `CLAUDE.md`
- The target spec file under `specs/deep_specs/`.
- Any sibling specs cited in the reason (e.g., if the bump touches
  a contract, also read the design doc and any ADRs that depend on
  it for cross-consistency).

## Workflow

1. Parse `args` into `spec`, `bump_kind`, `reason`.
2. Locate the spec at `specs/deep_specs/<spec>` (glob if needed).
3. Detect the document's existing revision surface in this order:
  - a `**Version:** X.Y.Z` field
  - a `| Version | X.Y.Z |` table cell
  - a `**Decision History:**` section (the format used by the
    scaffolded ADRs)
4. If a numeric version is present, compute the new version with
  SemVer:
  - `patch`: `1.2.3` -> `1.2.4`
  - `minor`: `1.2.3` -> `1.3.0`
  - `major`: `1.2.3` -> `2.0.0`
5. Update only the detected numeric version field/cell when one
  exists.
6. Append a new dated history entry using the document's existing
  history style:
  - ADR `**Decision History:**` entries stay bullets
  - Revision History tables stay tables
7. If the spec cites test counts, re-enumerate distinct IDs from
   the source and label counts as `collected` vs `passed+skipped`.
8. Run `make marker-scan` — the new revision entry must not
   introduce forbidden markers (`CRIT-001`).

## Rules

- Never edit prior revision-history entries. Append only
  (`IMP-001`).
- If the document has no numeric version surface, do not invent
  one. Append the history entry only and report `old_version` and
  `new_version` as `null`.
- Never rewrite the document into a different history format just
  to satisfy this command.
- Never edit version numbers anywhere other than the existing
  version surface and the new history entry.
- If the change alters contract semantics, the bump kind must be
  `major` and the operator must confirm.

## Report

```json
{
  "spec": "specs/deep_specs/...",
  "old_version": "...",
  "new_version": "...",
  "history_entry_added": true,
  "marker_scan": "pass|fail"
}
```
