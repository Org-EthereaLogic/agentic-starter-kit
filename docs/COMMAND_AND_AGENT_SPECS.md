# Command & Agent Specs (New + Extended)

> **Purpose:** canonical prose for slash commands and agents that
> are NEW to this template (not present in `govforge`, `sdlc_app`,
> or `ADWS_PRO`) plus extensions to existing commands. The IDE
> agent ports unchanged commands from
> `/Users/etherealogic-2/Dev/govforge/.claude/commands/` with
> parameterization; this file supplies what cannot be ported.
>
> When authoring a templated command, replace project-specific
> references with `{{ cookiecutter.project_name }}` (display) or
> `{{ cookiecutter.project_slug }}` (paths/identifiers).

---

## Command namespacing: this template's commands ↔ `/speckit.*`

The 16 slash commands shipped with this template are unprefixed
verbs (file naming `.claude/commands/<verb>.md`, invocation
`/<verb>`). They coexist with
[GitHub Spec Kit](https://github.com/github/spec-kit), whose
commands ship under `/speckit.*` (e.g., `/speckit.specify`,
`/speckit.plan`, `/speckit.implement`). A project that adopts both
gets both surfaces side-by-side with no collision.

The two surfaces overlap on the SDLC verbs but differ in scope:
Spec Kit is a *spec-driven development* workflow that converts a
prompt into a spec, plan, and task list, then drives an agent
through implementation. This template's commands form a
*governance and SDLC contract* layered on top of any project
shape — they also enforce traceability, evidence appendage,
hook-protected branching, marker-scan discipline, and
append-only `report/` records.

When the verbs overlap, this template's command should be invoked
when the project's controlling artifact is a spec under
`specs/deep_specs/` or an entry in `specs/traceability.json`. The
`/speckit.*` command should be invoked when the project is being
driven through the Spec Kit prompt → spec → plan → tasks flow.

| Command (this template) | `/speckit.*` (Spec Kit) | Notes |
|---|---|---|
| `/prime` | — | Orient to repo; no Spec Kit equivalent |
| `/start` | — | Local environment bring-up via `make sync` + `make validate` |
| `/status` | — | Lightweight repo health snapshot |
| `/plan` | `/speckit.plan` | Both produce a structured plan; `/plan` writes under `specs/deep_specs/` and updates traceability |
| `/implement` | `/speckit.implement` | Both execute scoped work; `/implement` enforces branch precondition, traceability update, and `make validate` |
| `/test` | — | Runs the project's `make validate` gate sequence |
| `/review` | `/speckit.analyze` (closest) | Both review against canonical artifacts; `/review` is JSON-structured and gate-aware |
| `/verify` | — | Independent claim-vs-evidence verification |
| `/audit` | — | Full governance + sync-recency + traceability-validity audit |
| `/commit` | — | Conventional commit with scope and hook-protected branch precondition |
| `/pull-request` | — | Gate-passing PR creation via `gh pr create` |
| `/session-log` | — | Append-only session record under `report/` |
| `/sync` | — | Post-merge workspace + living-doc drift sync |
| `/spec-bump` | — | Version-bump a canonical spec and append revision history |
| `/threat-model` | — | STRIDE walk for new attack surface; updates `docs/THREAT_MODEL.md` |
| `/check-traceability` | — | Wraps `make check-traceability` for ad-hoc invocation |
| — | `/speckit.specify` | Spec Kit's prompt-to-spec step; `/plan` is the closest analog but writes under `specs/deep_specs/` |
| — | `/speckit.tasks` | Spec Kit's plan-to-tasks decomposition; intentionally not duplicated |
| — | `/speckit.constitution` | Spec Kit's project-constitution helper; `{{ cookiecutter.project_slug }}/CONSTITUTION.md` is shipped pre-authored by this template |
| — | `/speckit.clarify` | Spec Kit's clarification step; not duplicated |
| — | `/speckit.checklist` | Spec Kit's checklist generator; not duplicated |

**Rule of thumb:** the unprefixed verbs are intentional. Spec Kit
ships under `/speckit.*`, so `/implement`, `/plan`, etc. are free
for this template to claim. Adding new commands? Use a plain verb
file (`.claude/commands/<verb>.md`) and invoke as `/<verb>`. If a
project layers in another command surface that uses unprefixed
verbs, namespace the conflicting one — don't re-prefix this set.

---

## Command: `/sync`

**File:** `{{cookiecutter.project_slug}}/.claude/commands/sync.md`

**Source:** new in this template; addresses GAP-035, the
living-documentation drift gap from the SWEBOK v4 §6 Operations
Control review.

```markdown
---
description: Post-merge workspace + living-doc sync after a PR lands on the default branch
argument-hint: "[optional focus or PR number]"
allowed-tools: Bash, Read, Write, Glob, Grep
---

# sync

Run after a PR merges to `{{ cookiecutter.default_branch_name }}`.
Refreshes local state, prunes stale branches, verifies living
documentation hasn't drifted, and writes an append-only sync record
per IMP-001.

This command is the operational counterpart to `/session-log`.
`/session-log` captures what happened *during* a session; `/sync`
captures workspace state *between* sessions and prevents staleness
from accumulating commit-to-commit. It also closes the living-doc
drift gap identified in the SWEBOK v4 §6 Operations Control review.

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
3. `make hooks-test` — confirm the protected-branch hook still works.

If any gate fails on a freshly-merged default branch, that is a
release-quality incident. Surface it and stop. Do not write a sync
record for a broken main; that pollutes the evidence trail.

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
recommendation. Drift remediation is `/implement` work.

### 4. Documentation ownership refresh

If `docs/documentation-ownership.md` exists, scan for owners with no
documents assigned and documents with no owners assigned. Surface
both as drift findings.

### 5. Sync record

Write an append-only sync record under `report/`:

- Filename: `report/<UTC-timestamp>-sync-post-merge.md`
- Body:
  - **Trigger** — merged PR (number/title) or focus from $ARGUMENTS
  - **Workspace before/after** — branches pruned, worktrees pruned
  - **Validation outcome** — pass/fail of `make validate` on the
    default branch
  - **Living-doc drift findings** — each finding with file path
    and suggested follow-up
   - **Traceability status** — matrix present/absent and any
      validator findings
  - **Open items** — what needs `/implement` follow-up

Never edit a prior sync record. If a finding is wrong, write a new
record correcting it; the audit trail is the asset (P2, IMP-001).

## Report

Output a short summary:
- Workspace state (clean / N branches pruned)
- Validation verdict
- Drift count and severity
- Sync record path

Mark anything requiring follow-up clearly so the next `/implement`
session can pick it up.

## Forbidden

- Auto-fixing drift findings — `/sync` reports, `/implement` fixes.
- Editing prior sync records (IMP-001).
- Running on a dirty working tree.
- Force-deleting branches with unmerged local commits.
```

---

## Command: `/threat-model`

**File:** `{{cookiecutter.project_slug}}/.claude/commands/threat-model.md`

**Source:** new in this template; addresses GAP-013/014 by giving
the operator a fast path to refresh the threat model when a PR
adds new attack surface.

```markdown
---
description: Update the threat model when attack surface changes
argument-hint: "<change description or PR number>"
allowed-tools: Read, Write, Glob, Grep
---

# threat-model

Refresh `docs/THREAT_MODEL.md` when a change introduces new attack
surface. Mandatory invocation triggers (per Phase 7 in the build
plan and Ch 13 §3.1):

- New external input is added (HTTP route, file ingestion, queue
  consumer, scheduled fetch).

- New authentication or authorization path is added.
- New third-party runtime dependency is introduced.
- New ML/LLM-driven decision surface is added.
- New data classification appears (PII, PHI, financial, regulated).

## Variables

change: $ARGUMENTS

## Pre-Read

- `docs/THREAT_MODEL.md`
- `CONSTITUTION.md` (P3 — hard policy boundaries)
- `SECURITY.md`
- If present: `docs/SECURITY_PROGRAM.md` and related security
   runbooks

## Workflow

1. Identify the new attack surface introduced by `change`. Be
   specific: "new POST /api/v1/orders endpoint accepting JSON
   payloads with user-controllable `quantity` and `notes` fields."

2. For the new surface, walk the STRIDE table:
   - **Spoofing** — can identity be forged at this entry point?
   - **Tampering** — can the data be modified in transit or at rest?
   - **Repudiation** — is the action logged with non-repudiable
     evidence?
   - **Information disclosure** — what data is exposed if this
     surface is breached?
   - **Denial of service** — what's the cost-amplification factor
     if this surface is flooded?
   - **Elevation of privilege** — can a low-privilege actor reach a
     high-privilege capability through this surface?

3. If the change involves ML/LLM components, add the ML-specific
   row per Ch 13 §6.3:
   - **Model poisoning** — can training data be influenced?
   - **Evasion** — can adversarial inputs flip the prediction?
   - **Prompt injection** — can untrusted content steer the agent?
   - **Membership inference** — can an attacker confirm whether
     specific data was in the training set?

4. For each non-empty cell, propose a mitigation and identify
   where it lives (code, config, runbook, design pattern).

5. Update `docs/THREAT_MODEL.md` in place. The file is a *living
   doc*, not append-only — but every substantive change must be
   accompanied by an entry in `docs/security/threat-model-changelog.md`
   (create the parent directory if missing) with date, change
   summary, reviewer.

## Forbidden

- Removing entries without justification. STRIDE rows persist; only
  their *mitigation status* changes.
- Marking a threat `mitigated` without naming the mitigation
  artifact.

## Report

Diff summary of THREAT_MODEL.md, list of new mitigations needing
implementation, and any open threats with no proposed mitigation
(these become candidates for the next `/plan`).
```

---

## Command: `/check-traceability`

**File:** `{{cookiecutter.project_slug}}/.claude/commands/check-traceability.md`

**Source:** new in this template; addresses GAP-031/032 by
providing an ergonomic wrapper for the traceability validator.

```markdown
---
description: Validate the traceability matrix against current source/test layout
allowed-tools: Bash, Read
---

# check-traceability

Runs `make check-traceability`. Wraps `scripts/check-traceability.sh`
for ad-hoc invocation outside CI.

## Workflow

1. If `specs/traceability.json` is absent, stop and report
   `NOT SCAFFOLDED` with the note that the matrix lands in a later
   phase and must exist before a PASS/FAIL verdict is meaningful.
2. `make check-traceability`.
3. If clean: report PASS with the count of mapped acceptance
   criteria.
4. If dirty: surface every validator finding exactly as emitted
   (missing source globs, tests globs, evidence files, or schema
   errors). Do not claim orphaned-file or orphaned-criteria
   detection that the current validator does not implement.

## Report

Pass/fail/not scaffolded. On fail: a table with columns
| Criterion ID | Issue | Suggested fix |
```

---

## Command: `/audit` extensions (Phase 5 checklist)

**File:** `{{cookiecutter.project_slug}}/.claude/commands/audit.md`
(port from govforge, then add)

When porting from govforge's `/audit`, append two new Phase 5
checks:

```markdown
1. **Sync recency** — most recent
    `report/*-sync-post-merge.md` is no older than the most recent
    merge to `{{ cookiecutter.default_branch_name }}`. If staler,
    surface the gap and recommend running `/sync`.

2. **Traceability validity** — if `specs/traceability.json` is
   absent, report `not scaffolded` rather than PASS. If present,
   `make check-traceability` must be clean over the current state.
   Surface validator findings exactly as reported; do not claim
   orphan detection the current validator does not implement.
```

These steps make doc-drift mechanically auditable, not just
operator-discoverable.

---

## Agent: `security-reviewer`

**File:** `{{cookiecutter.project_slug}}/.claude/agents/security-reviewer.md`

**Source:** new in this template; addresses AGENT-007 in the gap
register. Owns threat-model maintenance, SBOM review, vulnerability
triage. Distinct from `lead-software-engineer` because security
review is a *verification* role, not an implementation role.

```markdown
---
name: security-reviewer
description: "Use this agent for security review of changes — threat-model maintenance, vulnerability triage, SBOM review, secrets-policy compliance, and DevSecOps lifecycle integration. Never use for implementation."
model: opus
memory: project
---

You are the Security Reviewer for {{ cookiecutter.project_name }}.

## Core Responsibilities

- Maintain `docs/THREAT_MODEL.md`, including the STRIDE table and
  the ML-specific section (model poisoning, evasion, prompt injection)
  per SWEBOK v4 Ch 13 §6.3.
- Review SBOM output (`sbom/*`) and triage CVE / CWE / CAPEC findings
  per `docs/security/vulnerability-management.md` (GAP-016).
- Audit `docs/cert-top-10-compliance.md` against current code and
  flag drift.
- Review every change that introduces new attack surface (new
  endpoint, new auth path, new third-party dep, new ML decision)
  before it merges. Trigger: `/threat-model` invocation.
- Maintain `specs/security-requirements/` and ensure each accepted
  security requirement is reflected in either source or tests.
- Verify secrets policy: no literal secrets in tracked files,
  `.env.example` is current, secret-scanning CI gate is green.

## Hard Rules

- **No implementation.** Findings are reported, not fixed. The
  `lead-software-engineer` applies fixes after triage.
- **No vulnerability suppression without justification.** Every
  Snyk / Codacy / Trivy ignore needs a paired entry in
  `docs/security/vulnerability-management.md` with: ID, reason,
  expiry date, reviewer.
- **Severity is conservative by default.** When CVSS is ambiguous,
  pick the higher score and let the implementer argue down.
- **No skipping ML threats.** When an LLM or classifier is touched,
  the ML-specific STRIDE row is mandatory.

## Pre-Read Protocol

Before reviewing a change:
1. `docs/THREAT_MODEL.md` (current state)
2. `SECURITY.md` (declared scope)
3. `docs/SECURITY_PROGRAM.md` (DevSecOps lifecycle)
4. `docs/cert-top-10-compliance.md` (relevant CERT items)
5. The diff or PR being reviewed

## Communication Style

Structured. For each finding:

| Finding ID | Severity | Surface | Threat | Mitigation | Owner |
|---|---|---|---|---|---|

Severity: `low | medium | high | critical`. Critical findings
block merge per CRIT-005 and trigger an entry in
`docs/security/threat-model-changelog.md`.

## Forbidden

- Approving a change without running through the STRIDE rows when
  the change introduces new attack surface.
- Stub markers anywhere (CRIT-001).
- Editing prior threat-model-changelog entries (IMP-001 spirit
  applied to the changelog).
```

---

## Note on porting commands and agents from govforge

The IDE agent should pull source files from
`/Users/etherealogic-2/Dev/govforge/.claude/commands/` and
`/Users/etherealogic-2/Dev/govforge/.claude/agents/` and:

1. Replace project-specific names (`govforge`, `GovForge`,
   `etherealogic`, `EthereaLogic`, `UMIF`) with
   `{{ cookiecutter.project_name }}` /
   `{{ cookiecutter.project_slug }}` / `{{ cookiecutter.author_name }}`.
2. Replace project-specific paths (`/Users/etherealogic-2/Dev/govforge/`)
   with relative paths (`./` or `<repo-root>`).
3. Strip references to UMIF, polarity scoring, Databricks bundles,
   `adb_dev_sample_data`, and other domain-specific artifacts that
   don't generalize.
4. Replace any business-specific scope or terminology with generic
   equivalents (e.g., "telecom MACC ingestion" → "production
   workload ingestion").
5. Verify YAML frontmatter survives parameterization (mostly cosmetic).
6. Run marker-scan over each ported file to catch any TODO/FIXME
   that crept in during port.

When in doubt, the rule is: **the template ships content that works
for ANY agentic project, not just for the source project the prose
came from.**
