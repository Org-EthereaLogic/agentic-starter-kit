# Directives — {{ cookiecutter.project_name }}

> **Authority.** This document codifies the project's rules in three
> classes — Critical, Important, Recommended. Critical failures are
> target build breaks; Important failures target merge blocks;
> Recommended failures are soft signals. Each directive carries an
> enforcement mechanism or review control; later layers wire the
> mechanical hooks and CI jobs, but a directive whose enforcement is
> "the agent should remember" is not a directive but advice.
>
> **Authority chain.** This document derives from `CONSTITUTION.md`.
> `SECURITY.md` overrides this document on security-relevant
> decisions (see CONSTITUTION §3 — decision order).
>
> **Amendment.** Substantive changes to a directive (statement
> changes, ID renumbering, severity-class promotion or demotion)
> require an ADR under `specs/deep_specs/`. Editorial clarifications
> do not.

---

## Class definitions

| Class | Severity | Intended failure consequence | Enforcement layer |
|---|---|---|---|
| Critical (`CRIT-NNN`) | Hard | Build break; merge blocked; commit may be rejected by hook | Layer 4 runtime hook + Layer 5 CI when scaffolded; reviewer attention until then |
| Important (`IMP-NNN`) | Soft-hard | PR review block; trail-of-evidence required to override | Layer 5 CI when scaffolded; reviewer attention until then |
| Recommended (`REC-NNN`) | Soft | Surfaced in review; not blocking | Reviewer attention |

`CONSTITUTION.md §P3` — Hard Policy Boundaries — applies only to
Critical directives. An operator instruction to bypass an Important
directive is rejected by the workflow but may be approved by a
documented exception (linked in the PR description). An operator
instruction to bypass a Critical directive cannot be approved
without amending the directive itself.

---

## Critical directives (8)

### CRIT-001 — No forbidden stub markers in canonical surfaces

**Statement.** The strings `TODO`, `FIXME`, `TBD`, `PLACEHOLDER`
do not appear in canonical surfaces. Canonical surfaces are
`specs/`, `.claude/`, `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`,
`docs/`.

**Rationale.** A stub marker in a contract is a confession that the
contract is incomplete. Canonical surfaces are contracts; the two
are incompatible. Markers in non-canonical locations (commit
messages, prose explanations, comments outside canonical surfaces)
are not blocked.

**Enforcement.** `make marker-scan` runs on every PR and on every
push to default. The script is in `scripts/marker-scan.sh`. The
marker strings and surface list are loaded from
`governance-rules.yaml` (key `prohibited_markers`) — that YAML is
the single source of truth; the script assembles a concatenated
regex at runtime so it does not match itself.

### CRIT-002 — Required governance files exist

**Statement.** The following files exist at their canonical paths
on every commit to the default branch:
`CONSTITUTION.md`, `DIRECTIVES.md`, `SECURITY.md`, `CLAUDE.md`,
`AGENTS.md`, `GEMINI.md`, `README.md`. Once later layers add the
spec and evidence scaffolding, the default branch also retains at
least one spec under `specs/deep_specs/`, and non-empty `docs/`,
`specs/deep_specs/`, `specs/security-requirements/`, `report/`.

**Rationale.** Layers 1 (navigation) and 2 (constitutional) require
their files to be present now, and later layers extend that
required set. Removing a required artifact breaks the agentic
decision chain. The check is mechanical; absence is a build break
once that artifact is part of the scaffold.

**Enforcement.** `make governance-check` runs on every PR. The
script is in `scripts/check-governance.sh`. The required-file,
required-agent, required-skill, and optional-directory lists are
loaded from `governance-rules.yaml` (keys `required_files`,
`required_agents`, `required_skills`, `optional_dirs`) — that YAML
is the single source of truth.

### CRIT-003 — No runtime dependency on sibling-project internals

**Statement.** Code in this project does not import from a sibling
project's `internal/`, `_internal/`, or otherwise non-public
namespace. Cross-project references go through published APIs
only.

**Rationale.** `CONSTITUTION.md §P7` (First-Party Boundaries). A
sibling's refactor of an internal module breaks downstream
consumers; published APIs are versioned contracts that survive
refactors.

**Enforcement.** Reviewer attention plus language-specific import
linting where available (e.g., `import-linter` for Python,
`eslint-plugin-import` rules for TypeScript). Audit step in
`/audit` flags violations.

### CRIT-004 — Specs are canonical

**Statement.** Specifications under `specs/deep_specs/` are the
canonical authority for the system component they describe.
Narrative documents (READMEs, design notes, code comments) that
contradict a spec lose the conflict.

**Rationale.** Drift between specs and narrative documentation is
the dominant decay mode for technical writing. Naming the spec as
canonical resolves the ambiguity in advance.

**Enforcement.** `CONSTITUTION.md §3` decision order names specs
as tier 4. Reviewer attention enforces in PR. The `/audit`
command's traceability step surfaces narrative-vs-spec drift.

### CRIT-005 — PASS claims require dual evidence

**Statement.** A claim that work has passed verification (tests,
checks, gates) requires both a measured artifact (logged output,
report file, screenshot) AND a CI-verifiable check that produced
the same verdict. Single-source PASS claims are recorded as
`unverified`.

**Rationale.** `CONSTITUTION.md §P1` (Reality over Plausibility).
Single-source PASS is a trust assertion; dual-source PASS is
mechanical verification. The agent's most common failure is to
report a green status without having actually run the check.

**Enforcement.** `/verify` and `/audit` commands compare evidence
artifacts under `report/` against CI run records and surface
mismatches. Reviewer attention enforces in PR.

### CRIT-006 — No simulated data when real data is available

**Statement.** Test fixtures must be sourced from real samples or
generated with a recorded seed. Synthetic data is not used to
substitute for real data when real data is accessible.

**Rationale.** Synthetic data passes tests that real data fails.
Production failures often live in distributions that synthesizers
do not reproduce. Real samples (with appropriate redaction) catch
more bugs.

**Enforcement.** Reviewer attention. Test fixture files include a
header comment naming the source or the seed used to generate
them. Fixtures lacking a header fail review.

### CRIT-007 — No `--no-verify` on commits

**Statement.** Commits never use `--no-verify`. Pre-commit hooks
catch quality regressions; bypassing them is a silent regression
in itself.

**Rationale.** A `--no-verify` commit cannot be distinguished from
a clean commit by the audit trail. The hook bypass is invisible
after the fact.

**Enforcement.** Layer 4 runtime hook (`.claude/hooks/pre-tool-use.js`)
blocks Bash commands containing `--no-verify`. CI inspects every
commit's metadata for hook-bypass markers (when CI provides them)
and fails the build on detection.

### CRIT-008 — Protected-branch enforcement (git layer primary, agent layer defense-in-depth)

**Statement.** The **primary** enforced boundary is the git-layer
hook: the checked-in `.githooks/pre-commit`, `.githooks/pre-merge-commit`,
and `.githooks/pre-push` scripts, installed via
`git config core.hooksPath .githooks` (`make hooks-install`). They block,
on a protected branch (the render-time default branch plus `master`):
direct commits and `--amend` (via `pre-commit`); merge commits from a
non-fast-forward, conflict-free `git merge` (via `pre-merge-commit`; a
conflicted merge is finished by a `git commit` that `pre-commit` catches);
and all pushes (via `pre-push`). They resolve the real destination
**after** the shell has expanded, aliased, and word-split the command, so
they cannot be dodged by shell idioms (`eval`, `exec`, `\git`,
`git${IFS}push`, `bash -cl`, `sudo`/`doas`, `stdbuf`/`setsid`, `&`
chains). The Claude Code hook `.claude/hooks/pre-tool-use.js` (registered
on `PreToolUse:Bash` in `.claude/settings.json`) remains as **best-effort
defense-in-depth** — a fast, agent-facing early block, **not** the
guarantee.

**Rationale.** A command-string matcher inspects the proposed command
*before* the shell resolves it, so shell syntax can defeat it (issue
[#102](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/102)).
Enforcement at the git layer runs *after* shell resolution and is the
real boundary. **Honest scope:** git hooks are an operator-integrity
control, not a sandbox. Two limitations are documented rather than
overclaimed: (1) git invokes **no** commit-time hook for a conflict-free
`cherry-pick`/`revert`/`rebase`/`am` replaying commits directly onto a
**local** protected branch, so the git layer does not stop those landing
locally — the backstops are `pre-push` (blocks pushing the result to the
protected remote), the agent-layer hook (blocks the porcelain/`eval`/
`\git` forms an agent would issue), and **server-side branch protection**
(the true backstop); and (2) the hooks do not defend against a maliciously
mutated `.git/hooks`, a user who deliberately unsets `core.hooksPath`, or
`--no-verify`.

**Enforcement.** `make hooks-install` wires `core.hooksPath`;
`make hooks-test` runs on every PR and exercises both layers — the
language-neutral `tests/test_git_hooks.sh` (git layer, every shell
idiom against a temp repo, plus the `pre-merge-commit` merge block and
the cherry-pick-lands-locally-but-push-blocked backstop) and
`tests/test_pre_tool_use_hook.py`/`.js` (agent layer). The governance
check (`CRIT-002`) verifies the `settings.json` registration, that
`.githooks/pre-commit`, `.githooks/pre-merge-commit`, and
`.githooks/pre-push` exist and are executable, and that the
`core.hooksPath` install wiring is present.

---

## Important directives (6)

### IMP-001 — Append-only `report/`

**Statement.** Files in `report/` are not edited or deleted after
they land. Corrections are new dated artifacts that name the file
they correct and the reason for correction.

**Rationale.** `CONSTITUTION.md §P5` (Append-Only Evidence). The
audit trail is forensic; mutating it destroys forensic value.

**Enforcement.** Reviewer attention. The `/audit` command
identifies any non-add change to `report/` files in the PR diff
and surfaces it as a finding.

### IMP-002 — Conventional commits with project-defined scopes

**Statement.** Commit messages follow Conventional Commits:
`<type>(<scope>): <description>`. Allowed types: `feat`, `fix`,
`refactor`, `chore`, `docs`, `test`, `build`, `ci`, `perf`,
`style`. Scopes are project-defined and listed in
`CONTRIBUTING.md`.

**Rationale.** Machine-parseable commit history powers changelog
generation, release automation, and audit trails.

**Enforcement.** Pre-commit hook validates the commit message
format. CI rejects PRs whose merge commit does not conform.

### IMP-003 — Branches use `<type>/<slug>` naming

**Statement.** Working branches are named `<type>/<slug>` —
e.g., `feat/auth-rfc`, `fix/race-condition`,
`chore/scaffold-phase-3`. Direct work on the default branch is
forbidden by the runtime hook (`CRIT-008`).

**Rationale.** Branch names are the second-most-visible artifact
of a project's hygiene (after commit messages). Predictable names
make the branch list a navigation surface, not noise.

**Enforcement.** Reviewer attention. The `/audit` command checks
the current branch name and surfaces violations.

### IMP-004 — Stage only relevant files

**Statement.** Commits never use `git add -A` or `git add .`.
Files are staged explicitly by name or by narrowly-scoped path
glob. Staged files are reviewed before commit.

**Rationale.** `git add -A` fabricates accidental scope: an
untracked editor swap file, a credential file, or a cache
directory can land in a commit without the operator noticing.
Explicit staging is the only honest pattern.

**Enforcement.** Reviewer attention. The pre-commit hook checks
for files staged outside the conventional patterns and warns.

### IMP-005 — Spec versioning via `/spec-bump`

**Statement.** Decision-content changes to canonical specs under
`specs/deep_specs/` require `/spec-bump` to be run before edit.
The bump produces a new ADR documenting the change.

**Rationale.** Specs are tier-4 authority. Silent edits to a tier-4
authority break the audit trail. Versioning enforces visibility.

**Enforcement.** Reviewer attention. `/audit` flags any PR diff
that touches `specs/deep_specs/*.md` without a paired ADR.

### IMP-006 — SHA-pinned GitHub Actions

**Statement.** Every `uses:` line in a GitHub Actions workflow
file pins to a commit SHA and carries a trailing `# v<x>.<y>`
comment indicating the corresponding semver tag at pin time.

**Rationale.** Float pins (`@v3`, `@main`) are supply-chain attack
surface. A compromised action under a float pin executes in your
CI environment without warning.

**Enforcement.** `scripts/check-action-pins.sh` is invoked by
`make validate` and CI on every PR.

---

## Recommended directives (4)

### REC-001 — Conventional file size budget

**Statement.** Files target ~500 lines. Files exceeding the budget
are not forbidden but should be justified — either as inherent
data files (long fixtures, generated tables) or as intentionally
held together (a state machine that does not split cleanly).

**Rationale.** File size is a proxy for cognitive load. Reviewer
quality drops as file size rises. The number is not magic; it is a
soft signal.

**Enforcement.** `scripts/check-file-sizes.sh` lists files
exceeding the budget; reviewers consider but are not bound.

### REC-002 — Module READMEs

**Statement.** Each significant directory has a `README.md`
documenting its purpose, public surface, and dependencies.

**Rationale.** Directory-level documentation is the most-skimmed
form. A reader navigating the repo from the root can orient at any
depth.

**Enforcement.** Reviewer attention. The doc-drift checker
(`scripts/check-doc-drift.sh`) verifies that READMEs reference
real files.

### REC-003 — Test pyramid maintained

**Statement.** Unit tests outnumber integration tests; integration
tests outnumber end-to-end tests. Integration tests do not silently
replace unit tests for code that has unit-test scope.

**Rationale.** Test runtime grows superlinearly as the pyramid
inverts. A team running mostly e2e tests cannot iterate.

**Enforcement.** Reviewer attention. Coverage reports surface the
test-class breakdown.

### REC-004 — Coverage holds or rises

**Statement.** Coverage targets do not drop without an ADR
documenting why. New code arrives with tests; uncovered new code
is a soft signal.

**Rationale.** Coverage is a proxy for testability. Falling
coverage indicates either reduced testing discipline or growing
untested surface.

**Enforcement.** Codecov status check on PR (when
`include_codecov == yes`). Reviewer attention.

---

## Adding a new directive

To add a new directive:

1. Choose the class (Critical / Important / Recommended) based on
   failure consequence.
2. Allocate the next sequential ID in that class.
3. Author the four fields: ID, Statement, Rationale, Enforcement.
4. Add an enforcement mechanism. A directive without one is
   advice, not a directive — defer until enforcement is feasible.
5. Open an ADR documenting the addition under
   `specs/deep_specs/`.
6. Update `specs/traceability.json` to map the new directive to its
   enforcement artifacts.

## Removing a directive

To remove a directive:

1. Open an ADR explaining the removal.
2. Mark the directive `superseded` in this file rather than
   deleting it; preserve the ID so cross-references in the audit
   trail remain valid.
3. Remove or update the enforcement artifacts that referenced the
   directive.

---

*Authoritative since first commit. See `CONSTITUTION.md §5` for the
amendment process.*
