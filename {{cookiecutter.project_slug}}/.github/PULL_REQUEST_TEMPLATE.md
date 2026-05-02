# Pull Request

## Summary

<one or two bullets stating what this PR changes and why>

## Directive IDs in play

<list any `CRIT-NNN`, `IMP-NNN`, or `REC-NNN` whose enforcement this PR
exercises or relaxes — e.g., `CRIT-008` for hook changes,
`IMP-002` for commit-format changes>

## Plan / Act / Verify / Report

### Plan

<scope, contract, acceptance criteria>

### Act

<files touched and why; cite directive IDs where applicable>

### Verify

- [ ] `make validate` passes locally
- [ ] `make hooks-test` passes locally (`CRIT-008`)
- [ ] `make check-traceability` passes (specs reference real source/tests/evidence)
- [ ] No stub markers in canonical surfaces (`CRIT-001`)
- [ ] No commit on `{{ cookiecutter.default_branch_name }}` or `master` (`CRIT-008`)
- [ ] No `--no-verify` used (`CRIT-007`)
- [ ] Conventional-commit format on every commit (`IMP-002`)
- [ ] Branch named `<type>/<slug>` (`IMP-003`)

### Report

<changed files, outcome, evidence path under `report/` if applicable>

## Cross-references

- Relevant spec: <`specs/deep_specs/<id>.md` or `specs/<type>-<slug>.md`>
- Threat-model impact: <none, or `docs/THREAT_MODEL.md` row added/updated>
- Traceability: <criterion IDs in `specs/traceability.json` touched>

## Risk class (per `CONSTITUTION.md §P8`)

- [ ] **Low** — docs / tests / refactor with green CI
- [ ] **Medium** — production-path code or schema change
- [ ] **High** — security policy, runtime hook, release engineering, or governance file change

If High, the corresponding agent autonomy mode for related work is
demoted to `Ask`. Confirm explicit operator approval below.
