---
name: run-validate
description: "Run `make validate` for {{ cookiecutter.project_name }} and surface each constituent gate's outcome verbatim, without summarising failures away."
paths:
  - "Makefile"
  - "Makefile.fragments/**"
  - "scripts/**"
  - "src/**"
  - "tests/**"
  - "specs/**"
  - "CONSTITUTION.md"
  - "DIRECTIVES.md"
  - "AGENTS.md"
  - "CLAUDE.md"
  - ".claude/**"
  - ".github/workflows/**"
---

# run-validate

Loads when the agent is about to change source, tests, scripts,
governance prose, hooks, or CI workflows in
{{ cookiecutter.project_name }}. Those are the surfaces that
`make validate` is designed to keep honest.

## What `make validate` runs

`make validate` aggregates these gates in order
(`Makefile` is authoritative; the fragment files define the
underlying targets):

1. `make marker-scan` — `CRIT-001`. Forbidden stub markers in
   canonical surfaces.
2. `make governance-check` — `CRIT-002`. Required governance
   files, folders, agent inventory, skill inventory.
3. `make check-traceability` — `specs/traceability.json` resolves
   to real source, real tests, and real evidence.
4. `make check-doc-drift` — paths mentioned in `docs/` and `specs/`
   exist in the repo.
5. `make hooks-test` — `CRIT-008`. Protected-branch hook
   regression suite.
6. `make lint` — language-specific linting.
7. `make typecheck` — language-specific type checking.
8. `make test` — language-specific test execution.

Coverage is separate. Run `make coverage` explicitly when the
operator needs coverage evidence.

## How to invoke

```sh
make validate
```

Run from the project root. The aggregate target stops at the first
failing gate by default (Make's `-k` is not used).

## Failure-handling rules

- **Report the failing gate's raw output.** Do not paraphrase. The
  operator must be able to tell which gate failed and why without
  re-running the command.
- **Do not silence a failure.** `CRIT-005` requires PASS claims to
  carry dual evidence; partial-pass and "expected to pass after my
  next change" are not acceptable substitutes.
- **Do not skip downstream gates.** When a gate fails, run the
  remaining gates explicitly so the report covers the full surface.
  Use the individual targets (`make marker-scan`, `make hooks-test`,
  …) rather than re-running `make validate`.
- **Coverage stays `unverified` unless `make coverage` was run
  explicitly.** `make validate` does not invoke coverage.

## Report format

Always report results as a checklist of the eight validate gates
above with one of three verdicts each:

- `passed` — the gate completed cleanly.
- `failed` — the gate exited non-zero. Include the first relevant
  error line and the path that triggered it.
- `not run` — the gate was skipped because an earlier gate failed
  and the operator opted not to continue. Never use `not run` to
  mean "I assumed it would pass".

Append the path to any new evidence file written under `report/`.

## Pre-conditions

- Working tree is on a non-protected branch
  (`{{ cookiecutter.default_branch_name }}` and `master` are
  blocked by `.claude/hooks/pre-tool-use.js` per `CRIT-008`).
- All language toolchains for the rendered project are installed.
  The Python path needs `uv` and the configured typechecker; the
  TypeScript path needs Node ≥ 20 and dependencies installed via
  `npm install` (`package-lock.json` exists only when the rendered
  project has one).

## See also

- `Makefile` and `Makefile.fragments/checks.mk` — the source of
  truth for what `validate` aggregates.
- `AGENTS.md` `Required checks` — the operator-facing list of the
  gates this skill wraps.
- `audit-trail-tail` skill — companion for inspecting what the
  hooks recorded while `make validate` was running.
