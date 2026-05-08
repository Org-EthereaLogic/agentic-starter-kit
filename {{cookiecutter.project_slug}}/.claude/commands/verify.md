---
description: Independently verify a subject against primary evidence
argument-hint: "<claim, PR number, spec ID, or file path to verify>"
allowed-tools: Read, Glob, Grep, Bash
---

# verify

Independently verify a {{ cookiecutter.project_name }} subject
against primary evidence.

## Variables

subject: $ARGUMENTS

## Workflow

1. Identify what must be verified. If `subject` is a PR number, use
   `gh pr view`, `gh pr diff`, and `gh api` for check-run details;
   if a spec ID, locate the canonical document under
   `specs/deep_specs/`; if a claim, find the source of the claim
   first.
2. Read the primary sources directly: `specs/`, implementation or
   config files, test files, or evidence artifacts under `report/`.
3. Trace dependencies and supporting surfaces.
4. Run relevant commands that produce observable proof. Do not
   execute `make validate` as a substitute for verifying individual
   claims.
5. When claims involve counts (requirement IDs, tests, source
   files), enumerate the distinct IDs present in the source
   document — do not infer from ID ranges or rely on prior
   summaries.

## Report format

Structure findings as three labeled sections:

### Verified

Facts that hold, with `file_path:line_number` citations and commands
that produced observable proof.

### Issues Found

Claim-vs-reality gaps. For each: the original claim, the actual
state, and the specific evidence that contradicts the claim.

### Inconclusive

Items that could not be fully determined, with the specific next
step that would resolve them.

## Principles

- Evidence over inference (`P5`).
- Canonical `specs/` over narrative `docs/` (`CRIT-004`).
- No file modification during verification.
- No `pass` or `verified` claim without replayable proof
  (`CRIT-005`).
- Report the raw `make marker-scan` hit count and file locations —
  do not classify hits as "benign" or editorialize them away
  (`CRIT-001`).
