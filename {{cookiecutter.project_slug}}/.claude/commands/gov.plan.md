---
description: Create or update a structured implementation or design plan in specs/
argument-hint: "<plan topic or scope>"
allowed-tools: Read, Write, Edit, Glob, Grep
---

# gov.plan

Create a structured implementation or design plan for
{{ cookiecutter.project_name }}.

## Variables

prompt: $ARGUMENTS

## Required Pre-Read

Per `AGENTS.md` Required Pre-Read, read before writing a plan:

- `CLAUDE.md`
- `AGENTS.md`
- `CONSTITUTION.md`
- `DIRECTIVES.md`
- `SECURITY.md`
- `README.md`
- The relevant canonical specs under `specs/deep_specs/` (ADRs,
  RFCs, design docs).
- The `README.md` in any directory the plan will touch.

## Instructions

- Align the plan to the architecture documented in
  `docs/ARCHITECTURE.md` and the canonical spec set under
  `specs/deep_specs/`.
- Use RELATIVE paths only.
- Include explicit acceptance criteria (numbered, each mapped to an
  evidence source under `report/` or to a test identifier).
- Include a validation plan referencing `make validate`.
- Include a rollback section for any change that modifies contracts,
  hooks, evidence schema, or governance boundaries.
- If the task needs a new plan file, create it under
  `specs/deep_specs/` using the appropriate template
  (`adr-template.md`, `rfc-template.md`, or `design-template.md`)
  and a descriptive filename (e.g., `adr-NNNN-<slug>.md` or
  `rfc-NNNN-<slug>.md`).
- Update `specs/traceability.json` when the plan introduces new
  acceptance criteria.
- Delegate to subagent `sdlc-technical-writer` when the plan
  produces or updates canonical specs.

## Report

Return only the path to the created or updated plan file.
