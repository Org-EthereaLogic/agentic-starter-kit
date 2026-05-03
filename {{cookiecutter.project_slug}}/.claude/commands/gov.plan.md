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

Per `AGENTS.md` and `CLAUDE.md`, read before writing a plan:

- `SECURITY.md`
- `CONSTITUTION.md`
- `DIRECTIVES.md`
- `AGENTS.md`
- `CLAUDE.md`
- The relevant canonical specs under `specs/deep_specs/`.
- The `README.md` in any directory the plan will touch.
- `docs/MCP_POLICY.md` before changing `.mcp.json`.

## Instructions

- Align the plan to the architecture documented in the relevant
  ADRs and `specs/deep_specs/README.md`. If
  `docs/ARCHITECTURE.md` exists, treat it as the stronger
  architecture index.
- Use RELATIVE paths only.
- Include explicit acceptance criteria (numbered, each mapped to an
  evidence source under `report/` or to a test identifier).
- Include a validation plan referencing `make validate`.
- Include a rollback section for any change that modifies contracts,
  hooks, evidence schema, or governance boundaries.
- If the task needs a new plan file, create it under
  `specs/deep_specs/` using the existing local convention. ADRs
  use `ADR/0001-adr-template.md`; RFC/design plans should follow
  the nearest existing deep-spec format in their subdirectory, or
  a descriptive Markdown file when no dedicated template is
  scaffolded yet.
- Update `specs/traceability.json` when it exists or when the task
  is explicitly scaffolding it. If the matrix is not present yet,
  call out the follow-up instead of claiming it was updated.
- Delegate to subagent `sdlc-technical-writer` when the plan
  produces or updates canonical specs.

## Report

Return only the path to the created or updated plan file.
