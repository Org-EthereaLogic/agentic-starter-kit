---
description: Generate and execute a scoped conventional commit for the current diff
argument-hint: "[optional message hint]"
allowed-tools: Bash, Read
---

# gov.commit

Generate and execute a scoped conventional commit for the current
diff.

## Variables

message_hint: $ARGUMENTS

## Pre-commit snapshot

- Branch: !`git branch --show-current`
- Status: !`git status --short`
- Diff summary: !`git diff HEAD --stat`

## Instructions

- If branch is `{{ cookiecutter.default_branch_name }}` or `master`,
  stop — create a `feat/...`, `fix/...`, or `chore/...` branch first.
  The repo `PreToolUse` hook will block it anyway (`CRIT-008`).
- Generate a conventional commit: `<type>(<scope>): <description>`.
- Types: `feat`, `fix`, `chore`, `docs`, `test`, `refactor`.
- Pick a `<scope>` from the directories most affected by the diff
  (e.g., `scaffold`, `specs`, `docs`, `claude`, `hooks`, `ci`,
  `agents`, `commands`, `tests`).
- Present tense, 50 characters or less, no trailing period.
- Stage only relevant files (do not `git add -A` / `git add .`).
- Never use `--no-verify` (`CRIT-007`).
- Never amend a prior commit (`IMP-001` spirit applied to history).

## Cherry-pick safety

If the commit being created is a cherry-pick, run `git show --stat HEAD`
after the cherry-pick and confirm every file mentioned in the
original message is present in the new diff. Rewrite the message if
not — the message must describe only what this commit actually
changes.

## Report

Return the commit hash and the commit message used. Separate
measured facts (files touched, hash) from interpretation (what the
change accomplishes) per `P5`.
