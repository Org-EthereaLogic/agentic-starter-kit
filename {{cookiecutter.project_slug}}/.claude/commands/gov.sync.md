---
description: Post-merge workspace + living-doc sync after a PR lands on the default branch
argument-hint: "[optional focus or PR number]"
allowed-tools: Bash, Read, Write, Glob, Grep
---

# gov.sync

Run after a PR merges to `{{ cookiecutter.default_branch_name }}`.
Refreshes local state, prunes stale branches, verifies living
documentation hasn't drifted, and writes an append-only sync record
per `IMP-001`.

This command is the operational counterpart to `/gov.session-log`.
`/gov.session-log` captures what happened *during* a session;
`/gov.sync` captures workspace state *between* sessions and
prevents staleness from accumulating commit-to-commit. It also
closes the living-doc drift gap identified in the SWEBOK v4 §6
Operations Control review.

## Variables

focus: $ARGUMENTS

## Pre-sync snapshot

- Current branch: !`git branch --show-current`
- Working tree: !`git status --short`
- Most recent merge: !`git log --merges -1 --pretty=format:'%h %s (%cr)'`

## Workflow

### 1. Workspace hygiene

1. Confirm working tree is clean. If not, stop — uncommitted work
   should not be silently swept away by a sync.
2. Switch to default branch:
   `git checkout {{ cookiecutter.default_branch_name }}`.
3. Pull with prune: `git pull --prune`.
4. List local branches whose upstream is gone:
   `git branch -vv | grep ': gone]' || true`.
5. For each gone-upstream branch, prompt before deleting. Never
   delete branches with unmerged local commits.
6. Prune worktrees for deleted branches: `git worktree prune`.

### 2. Validation re-run on the new default branch

1. `make sync` — refresh deps in case the merged PR changed them.
2. `make validate` — confirm merged default branch is green from a
   clean state.
3. `make hooks-test` — confirm the protected-branch hook still works
   (`CRIT-008`).

If any gate fails on a freshly-merged default branch, that is a
release-quality incident. Surface it and stop. Do not write a sync
record for a broken default branch; that pollutes the evidence
trail.

### 3. Living-doc drift check

For each living document, verify it still reflects current reality:

1. **Specs reference real files.** For every file path mentioned in
   `specs/deep_specs/*.md`, confirm the path exists in the repo.
   Run `scripts/check-doc-drift.sh warn` (or
   `make check-doc-drift`) and interpret the findings that
   originate from `specs/`. The script always scans both `docs/`
   and `specs/`; it cannot be scoped to a single subtree.
2. **ADR status is current.** No `accepted` ADR should reference a
   `superseded` ADR without itself being superseded. No spec should
   sit in `proposed` for more than 30 days without a status update.
3. **Directory READMEs match contents.** For each module directory
   with a README, confirm the listed files reflect actual contents.
4. **OPERATIONS.md is current** if that file is scaffolded and the
   merged PR touched anything under `.github/workflows/`,
   deployment configs, or release tooling.
5. **THREAT_MODEL.md is current** if `docs/THREAT_MODEL.md` exists
   and the merged PR added new external inputs, new auth paths, or
   new third-party dependencies.
6. **ARCHITECTURE.md is current** if that file is scaffolded and
   the merged PR changed module boundaries, added components, or
   shifted deployment shape.
7. **Traceability matrix is current.** If
   `specs/traceability.json` exists, run `make check-traceability`
   and surface deltas. Otherwise note that the matrix is not yet
   scaffolded.

For each drift finding, do not auto-fix — surface it with a
recommendation. Drift remediation is `/gov.implement` work.

### 4. Documentation ownership refresh

If `docs/documentation-ownership.md` exists, scan for owners with no
documents assigned and documents with no owners assigned. Surface
both as drift findings.

### 5. Sync record

Write an append-only sync record under `report/`:

- Filename: `report/<UTC-timestamp>-sync-post-merge.md`
- Body:
  - **Trigger** — merged PR (number/title) or focus from
    $ARGUMENTS.
  - **Workspace before/after** — branches pruned, worktrees pruned.
  - **Validation outcome** — pass/fail of `make validate` on the
    default branch.
  - **Living-doc drift findings** — each finding with file path
    and suggested follow-up.
   - **Traceability status** — matrix present/absent and any
      validator findings.
  - **Open items** — what needs `/gov.implement` follow-up.

Never edit a prior sync record. If a finding is wrong, write a new
record correcting it; the audit trail is the asset (`IMP-001`).

## Report

Output a short summary:

- Workspace state (clean / N branches pruned).
- Validation verdict.
- Drift count and severity.
- Sync record path.

Mark anything requiring follow-up clearly so the next
`/gov.implement` session can pick it up.

## Forbidden

- Auto-fixing drift findings — `/gov.sync` reports,
  `/gov.implement` fixes.
- Editing prior sync records (`IMP-001`).
- Running on a dirty working tree.
- Force-deleting branches with unmerged local commits.
