---
description: Create a GitHub pull request for the current branch after all gates pass
argument-hint: "[target-branch] (default: {{ cookiecutter.default_branch_name }})"
allowed-tools: Bash
---

# gov.pull-request

Create a GitHub pull request for the current branch after verifying
all validation gates pass.

## Variables

target_branch: $ARGUMENTS (default: {{ cookiecutter.default_branch_name }})

## Branch precondition

!`git branch --show-current`

If the current branch is `{{ cookiecutter.default_branch_name }}` or
`master`, stop — commits to protected branches are blocked by the
`PreToolUse` hook (`CRIT-008`). Create a feature branch first.

## Run

1. Resolve `base_ref` to `target_branch` when provided;
  otherwise use `{{ cookiecutter.default_branch_name }}`.
2. `git diff origin/<base_ref>...HEAD --stat`
3. `git log origin/<base_ref>..HEAD --oneline`
4. `make validate` — must pass (expands to `marker-scan`,
   `governance-check`, `check-traceability`, `check-doc-drift`,
   `hooks-test`, `lint`, `typecheck`, `test`).
5. Push: `git push -u origin $(git branch --show-current)`.
6. Create PR: `gh pr create --title "<title>" --body "<body>" --base <target_branch>`.

If `make validate` fails, stop and fix before creating the PR.

## PR body contents

- **Summary** — 1–3 bullets on what and why.
- **Test plan** — checkbox list of how to verify.
- **Evidence** — links to `report/` artifacts created for this
  change, if any.
- **AC coverage** — bullet per acceptance criterion with
  `file_path:line` or test identifier for evidence. Mark
  unsupported ACs as `unverified`, not `passed` (`CRIT-005`).

## Report

Return ONLY the PR URL that was created.
