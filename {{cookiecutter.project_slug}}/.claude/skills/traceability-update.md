---
name: traceability-update
description: "Edit `specs/traceability.json` — the machine-readable matrix mapping acceptance criteria to source, tests, and evidence — so the change survives `make check-traceability`."
paths:
  - "specs/traceability.json"
  - "specs/traceability.schema.json"
  - "specs/deep_specs/**"
  - "specs/security-requirements/**"
  - "scripts/check-traceability.sh"
---

# traceability-update

Loads when the agent is about to add, rename, or retire an entry
in `specs/traceability.json`. The matrix is the contract between
canonical specs (`specs/deep_specs/`) and their evidence
(`src/`, `tests/`, `report/`); a stale matrix is a
`check-traceability` failure waiting to happen.

## Matrix shape

`specs/traceability.json` is a single JSON document:

```json
{
  "criteria": [
    {
      "id": "AC-001",
      "spec": "specs/deep_specs/<slug>.md",
      "source": ["src/<glob>.py"],
      "tests": ["tests/<glob>.py"],
      "evidence": ["report/<timestamped-record>.md"]
    }
  ]
}
```

`specs/traceability.schema.json`, when present, is the
authoritative schema. `scripts/check-traceability.sh` validates:

1. JSON well-formedness.
2. Conformance to the schema (when `ajv` is on `PATH`).
3. Every `source` and `tests` glob expands to ≥ 1 file.
4. Every `evidence` path exists exactly (no globs).

## Editing rules

- **One PR adds one criterion.** Bundling criteria across PRs
  makes the matrix harder to bisect when a glob goes stale.
- **`source` / `tests` are globs; `evidence` is exact paths.** The
  validator treats them differently — see
  `scripts/check-traceability.sh:71-101`.
- **Never delete a criterion that ships in a release tag.** Mark
  it retired by removing the entry only after the corresponding
  spec has been moved to `specs/deep_specs/retired/` (when that
  path exists in the rendered project) or the criterion has been
  formally superseded in an ADR.
- **Keep `id` stable.** Acceptance-criterion IDs flow into release
  notes and audit records; renaming an `id` breaks every prior
  citation.
- **Evidence paths must exist when committed.** The validator
  hard-fails on missing evidence; do not pre-stage criterion
  rows that point at evidence the same PR has not yet produced.

## Workflow

1. Read the spec under `specs/deep_specs/` and identify the
   acceptance criterion that needs a row.
2. Pick a stable `id` (`AC-NNN`, `SR-NNN`, or a project-specific
   prefix that already appears in the matrix).
3. Add the entry to `criteria[]`. Keep entries in `id` order.
4. Run `make check-traceability`. Fix any failing glob or
   missing-evidence finding before commit.
5. Update the spec or directory `README.md` if the new criterion
   changes operator-visible behavior.
6. When the change adds a new criterion family, update
   `specs/traceability.schema.json` to declare the prefix.

## Failure modes

| Validator finding | Likely cause | Fix |
| --- | --- | --- |
| `criterion <id> source glob matches no files` | renamed source without updating matrix | regenerate the glob or split the criterion |
| `criterion <id> tests glob matches no files` | tests deleted or moved | update the glob; do not lower coverage |
| `criterion <id> evidence file missing` | evidence path typo or pre-staged | write the evidence first, then add the row |
| `<matrix> is not valid JSON` | trailing comma, unquoted key | re-format with `jq . specs/traceability.json` |
| `<matrix> does not conform to <schema>` | new criterion prefix | add the prefix to the schema, or pick an existing one |

## Reporting

After every matrix edit, report:

- The added/changed/removed `id` values (enumerated, never
  inferred from a range).
- The `make check-traceability` outcome.
- Which `specs/deep_specs/` document the new entry traces to.

## See also

- `scripts/check-traceability.sh` — validator source.
- `specs/traceability.schema.json` — schema, when present.
- `DIRECTIVES.md` `CRIT-004` — specs are canonical; the matrix
  is the machine-readable view of that authority.
