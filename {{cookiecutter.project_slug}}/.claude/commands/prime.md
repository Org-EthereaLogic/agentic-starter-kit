---
description: Orient to the {{ cookiecutter.project_name }} repository before acting
argument-hint: "[optional session-focus hint]"
allowed-tools: Read, Bash, Glob, Grep
---

# prime

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
- `specs/deep_specs/README.md`

## Report

After reading, output a brief orientation summary:

- Project scope and current phase.
- Repository taxonomy and key surfaces (Layers 1–5 per
  `CONSTITUTION.md`).
- Methodology precedence (the six-tier decision order in
  `CONSTITUTION.md §3`).
- Quality-control integration status (Codacy, Codecov, Snyk, SBOM,
  Macaron) inferred from files and workflows present in the
  rendered project, not from template-only `cookiecutter.json`.
  When an integration surface is absent, mark it `not present` or
  `not scaffolded` instead of guessing the original option.
- Key files relevant to `session_focus` (if provided) or to the
  current task context inferred from branch and recent commits.
- Any open questions about scope or intent.

Do not make any changes during priming.
