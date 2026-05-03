---
description: Orient to the {{ cookiecutter.project_name }} repository before acting
argument-hint: "[optional session-focus hint]"
allowed-tools: Read, Bash, Glob, Grep
---

# gov.prime

Orient to the {{ cookiecutter.project_name }} repository before acting.

## Variables

session_focus: $ARGUMENTS

## Context snapshot

- Branch + status: !`git branch --show-current && git status --short`
- Recent history: !`git log --oneline -10`
- File inventory: !`git ls-files | head -200`

## Read

- `CLAUDE.md`
- `AGENTS.md`
- `CONSTITUTION.md`
- `DIRECTIVES.md`
- `SECURITY.md`
- `README.md`
- The index of `specs/deep_specs/`

## Report

After reading, output a brief orientation summary:

- Project scope and current phase.
- Repository taxonomy and key surfaces (Layers 1–5 per
  `CONSTITUTION.md`).
- Methodology precedence (the six-tier decision order in
  `CONSTITUTION.md §3`).
- Quality-control integration status (Codacy, Codecov, Snyk, SBOM,
  Macaron) per `cookiecutter.json` selections shipped into this
  project.
- Key files relevant to `session_focus` (if provided) or to the
  current task context inferred from branch and recent commits.
- Any open questions about scope or intent.

Do not make any changes during priming.
