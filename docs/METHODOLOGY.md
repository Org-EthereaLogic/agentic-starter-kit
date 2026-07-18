# Methodology — Agentic Engineering as Infrastructure

> A short essay on how to run agentic coding workflows without
> drift, fabrication, or silent quality regression. The companion
> template (`agentic-starter-kit`) is one concrete realization of
> this methodology, but the methodology survives without the
> template.

---

## 1. The problem

Coding agents drift. Given a prompt and a goal, an LLM-driven agent
will produce output that *looks* plausible — formatted, fluent,
confidently asserted — and is often *not actually true*. It will
cite functions that don't exist, pin versions it didn't measure,
report tests it didn't run, and mark work `done` when work is
half-finished. None of this is malice. It is the natural failure
mode of pattern completion when applied to a domain (software
engineering) where reality is mechanical and assertions are cheap.

The remedy in big-company environments is people: code reviewers,
release managers, security reviewers, on-call rotations, change
advisory boards. Each layer catches what the previous one missed.
Solo operators and small teams do not have those layers. A single
operator running an agent on a Friday afternoon is the engineer,
the reviewer, the release manager, the security review, and the
on-call. When the agent says `done`, "done" is what gets shipped.

The methodology in this document treats that asymmetry as the
design constraint. Governance cannot be advice — advice gets
politely ignored under deadline pressure. Governance has to be
*infrastructure*: mechanically enforced, runtime-blocking, and
auditable after the fact. The agent cannot violate a rule because
the rule's enforcement layer denies the action before it lands.

## 2. The thesis

Convert governance from documentation to infrastructure. Build five
layers of defense in depth. Have each layer assume the previous one
might fail. Author all of it before the first feature ships, so the
infrastructure is in place when (not if) the agent produces
plausible-but-wrong work.

The five layers are:

| Layer | Name                  | Failure mode it catches                            |
|-------|-----------------------|----------------------------------------------------|
| 1     | Navigation            | Agent reads the wrong files first                  |
| 2     | Constitutional        | Agent applies the wrong precedence to a conflict   |
| 3     | Agent specialization  | Agent picks the wrong tool for the task            |
| 4     | Runtime enforcement   | Agent attempts a forbidden action                  |
| 5     | External validation   | Agent reports completion without measurement       |

Each layer is independently useful. A team that adopts only Layer 1
gets agents that consistently read the right files first, which is
already a meaningful improvement over the default. A team that
adopts all five gets a system where most classes of agentic failure
are mechanically prevented.

## 3. The five layers

### Layer 1 — Navigation

`CLAUDE.md`, `AGENTS.md`, and `GEMINI.md` exist at the repository
root. Their content tells an arriving agent exactly what to read,
in what order, before taking any action. The reading order is not
incidental — it is the *decision precedence* used when authority
sources conflict.

The Linux Foundation [AGENTS.md](https://agents.md/) format is a
de-facto standard. CLAUDE.md and GEMINI.md are runtime-specific
twins for Anthropic's Claude Code and Google's Gemini CLI. The
content of all three is largely identical. The duplication is
deliberate: each runtime checks for its specific filename, and
fragmenting content into a single shared file with symlinks creates
fragility on Windows and across Git providers.

A navigation file's job is small but load-bearing. It says: read
`CONSTITUTION.md` first, then `DIRECTIVES.md`, then the relevant
spec under `specs/deep_specs/`, then the module README. It also
declares the **decision order**: when CONSTITUTION says one thing
and DIRECTIVES says another, CONSTITUTION wins. When DIRECTIVES
says one thing and a deep spec says another, DIRECTIVES wins —
unless the deep spec is a security spec, in which case
`SECURITY.md` wins everything. This precedence is documented once,
in one place, and every agent is told to read it before acting.

### Layer 2 — Constitutional foundation

`CONSTITUTION.md` declares the project's principles. Eight, in
order. When two principles disagree, the lower-numbered one wins.
Reality over plausibility. Evidence traceability. Hard policy
boundaries. Explicit failure. Append-only evidence. Smallest
sufficient change. First-party boundaries. Risk-class autonomy.

`DIRECTIVES.md` codifies the rules in three classes — Critical
(failure is a build break), Important (failure is a review block),
and Recommended (failure is a soft signal). Each directive has an
ID, a statement, a rationale, and an enforcement mechanism. The
ID matters: Critical directives are referenced by ID in the runtime
hook, in the CI workflow, and in the slash command frontmatter. A
directive whose enforcement is "the agent should remember" is not a
directive; it is advice.

`SECURITY.md` declares the disclosure process, supported versions,
and the agentic-specific scope (prompt injection, hook bypass,
agent-tooling supply chain). It is small and concrete. Its size is
not a measure of its importance; the threat model lives in
`docs/THREAT_MODEL.md` and is much larger. SECURITY.md is the
*entry point* — the file a researcher reads to know how to report
something — not the model itself.

### Layer 3 — Agent specialization

`.claude/agents/*.md` defines specialized subagents. Each agent has
a narrow scope, a curated system prompt, and a memory mode.
`lead-software-engineer` plans and implements. `sdlc-technical-writer`
writes documentation. `test-automator` builds test suites.
`security-reviewer` reviews threat models and SBOMs (and explicitly
does not implement). `python-pro` and `typescript-pro` are
language-specialist coders. `ux-delight-specialist` reviews
front-end work for the qualities that automated tooling cannot
catch.

The specialization matters because a single generalist agent will,
under load, blur the line between roles. A change that introduces
new attack surface will get a hurried security review from the
implementing agent — the same kind of rubber-stamp review that is a
recognized failure mode in human teams. The fix is the same in both
cases: the reviewer is a different role from the implementer, by
construction.

`.claude/commands/*.md` defines slash commands. A slash command is
a parameterized workflow with a curated tool allowlist. `/plan`
takes a goal and produces a plan spec. `/implement` takes a plan
spec and produces code plus tests. `/audit` runs a multi-step
inspection over the repo state. `/sync` runs after a PR merges to
refresh the workspace and detect documentation drift. `/threat-model`
walks the STRIDE table when a change introduces new attack surface.
The command files are short, declarative, and version-pinned —
their content is a *contract* with the operator's muscle memory.
Changes to a slash command's behavior are contract changes.

### Layer 4 — Runtime enforcement

`.claude/hooks/pre-tool-use.js` is a Node.js script that intercepts
every Bash tool call the agent makes. It examines the command and,
if the command matches a forbidden pattern, returns exit code 2
with a message describing the block. The agent sees the block,
adjusts, and tries again — typically by branching from `main`
instead of committing to it.

The forbidden patterns include: direct push to a protected branch,
refspec push to a protected branch, broad push modes (`--all`,
`--mirror`) when on a protected branch, commit on a protected
branch, commit-producing subcommands (`git commit-tree`), nested
shell escapes, and chained subcommands using `&&` / `;` / `||` /
backticks / `$()` that include a banned action. Every pattern
matters, because every pattern represents a real bypass an agent
has tried under real conditions.

The hook is short, paranoid, and tested. The test suite —
`tests/test_pre_tool_use_hook.py` and its TypeScript twin — is the
hook's contract. When a new bypass class is discovered, the test
case is added *first*, then the hook is updated, then the bypass
is closed. The order matters: tests-first ensures the regression
shield is built before the hole is patched. It also ensures the
test never accidentally drifts to allowing the bypass it was meant
to catch.

The hook is registered in `.claude/settings.json` as a
`PreToolUse:Bash` matcher. The settings file is short and JSON-only
(no comments — JSON does not support them, and the file is parsed
strictly). When the file is missing or the hook is unregistered,
Layer 5's `make hooks-test` target catches the mismatch and fails
the validation gate.

### Layer 5 — External validation

`Makefile` and `.github/workflows/ci.yml` provide the external
audit. The Makefile is the local interface; the CI workflow is the
remote one. They run the same gates, in the same order, against
the same code.

The gates are:

- `marker-scan` — no stub markers (TODO, FIXME, TBD, PLACEHOLDER)
  in canonical surfaces.
- `governance-check` — required governance files exist and
  required folders are populated.
- `check-traceability` — `specs/traceability.json` references real
  source files, real tests, and real evidence artifacts.
- `check-doc-drift` — paths mentioned in `docs/` and `specs/`
  exist in the repo.
- `lint`, `typecheck`, `test`, `coverage` — language-specific
  build hygiene.
- `hooks-test` — the protected-branch hook's regression suite is
  green.
- `secret-scan` — no literal secrets in tracked files.
- `sbom-generate` — CycloneDX SBOM is produced and uploaded as a
  CI artifact.

Every gate is independent. Every gate is reproducible locally
(running `make <gate>` produces the same answer as the CI job
running the same command). The CI workflow's only privilege over
the Makefile is access to deployment secrets and the ability to
upload artifacts; the validation logic is identical.

## 4. The constitutional principles

The eight principles, in their order of precedence:

1. **P1 — Reality over Plausibility.** Verified facts beat
   plausible narratives. Tool-call evidence beats agent assertions.
   "I ran the test" is not evidence; the test runner's output is.
2. **P2 — Evidence Traceability.** Every claim of completion is
   traceable to a measured artifact under `report/`. The audit
   trail is the asset. A commit message that says "tests pass" with
   no traceable evidence is a P1 violation; a commit message that
   says "tests pass — see report/2026-05-01-test-results.md" is
   compliant.
3. **P3 — Hard Policy Boundaries.** Some rules cannot be
   overridden by context, urgency, or instruction. Those are the
   Critical directives. An agent under deadline pressure is *more*
   bound by Critical directives, not less.
4. **P4 — Explicit Failure.** Errors propagate; they do not get
   silently swallowed. A bare `try/except` that returns an empty
   list when the API call fails is a P4 violation. A loud failure
   is preferable to a quiet wrong answer.
5. **P5 — Append-Only Evidence.** Once an evidence artifact lands
   in `report/`, it does not get edited or deleted. Corrections
   are *new* artifacts. The audit trail is forensic; mutating it
   destroys forensic value.
6. **P6 — Smallest Sufficient Change.** Speculative abstractions
   and premature generalization are quality regressions, not
   virtues. A bug fix does not need surrounding cleanup. A
   one-shot operation does not need a helper function. Three
   similar lines is preferable to a premature abstraction.
7. **P7 — First-Party Boundaries.** Runtime dependencies on
   sibling-project internals are forbidden. Cross-project
   references go through published APIs only. The boundary
   between two systems is a *contract*, not a courtesy.
8. **P8 — Risk-Class Autonomy.** The agent's level of autonomy is
   a function of the task's risk class. Low-risk work (docs,
   tests, refactors with green CI) runs in YOLO mode. Medium-risk
   work (production-path changes, schema migrations) runs in auto
   mode with a review checkpoint. High-risk work (security
   policies, the runtime hook itself, release engineering) runs in
   ask mode with explicit operator confirmation.

The order matters. When P1 and P6 conflict — when "verify by
running the test" requires writing a small helper that violates
P6's smallest-sufficient-change preference — P1 wins. When P2 and
P8 conflict — when an autonomous run wants to skip evidence capture
to save tokens — P2 wins. Lower number wins.

## 5. The eighteen directives

Eight Critical (`CRIT-001` through `CRIT-008`), six Important
(`IMP-001` through `IMP-006`), four Recommended (`REC-001` through
`REC-004`). Every directive has an ID, a statement, a rationale,
and an enforcement mechanism. The `DIRECTIVES.md` file is the
authoritative register. The high-impact directives are:

- **CRIT-001** No forbidden stub markers in canonical surfaces.
  Enforced by `make marker-scan`. A `TODO` is a confession that the
  work is incomplete; a canonical surface is a *contract*; the two
  are incompatible.
- **CRIT-005** PASS claims require dual evidence. A single-source
  pass is marked `unverified`. This is the directive that closes
  the "agent says tests pass without running them" failure mode.
- **CRIT-007** No `--no-verify` on commits. Pre-commit hooks catch
  regressions; bypassing them is a silent quality regression.
- **CRIT-008** Git-layer protected-branch guards are installed and
  tested, with the agent-layer hook retained as defense in depth.
  This is the directive that makes Layer 4 mechanically auditable
  by Layer 5.
- **IMP-001** Append-only `report/`. Implements P5 at the file-
  system level.
- **IMP-004** Stage only relevant files. `git add -A` and
  `git add .` fabricate accidental scope. Explicit staging is the
  only honest pattern.
- **IMP-006** SHA-pinned GitHub Actions. Every `uses:` line carries
  a `@<sha>` and a trailing `# v<x>.<y>` comment. Float pins are
  supply-chain attack surface.

The remaining directives are referenced by ID throughout the
template's commands, hooks, and CI configuration.

## 6. The SWEBOK v4 bridge

The IEEE Computer Society's *SWEBOK Guide v4.0a* (September 2025)
introduced three new Knowledge Areas: **Software Architecture**,
**Software Engineering Operations**, and **Software Security**. It
also added cross-cutting AI-assisted-development guidance under the
existing Construction KA (§4.16–4.17). Each is anchored explicitly
in the template:

- **Ch 2 — Software Architecture (IEEE 42010).** Anchored by
  `docs/ARCHITECTURE.md`. The document carries four named views —
  logical, process, deployment, data — plus a stakeholders-and-
  concerns table and an architecturally-significant decisions
  section that cross-references ADRs.
- **Ch 6 — Software Engineering Operations (ISO/IEC/IEEE
  32675:2022).** Anchored by `docs/OPERATIONS.md`. The document
  covers Operations Planning (capacity, availability, backup/
  recovery, DR, environments), Operations Delivery (release
  strategies — canary, blue-green, rolling — plus feature flags
  and rollback), and Operations Control (change management,
  incident management, continuous risk monitoring per IEEE 2675).
- **Ch 13 — Software Security.** Anchored by `docs/THREAT_MODEL.md`
  and `docs/SECURITY_PROGRAM.md`. The threat model carries a full
  STRIDE table plus a dedicated ML-specific section (model
  poisoning, evasion, prompt injection, membership inference) per
  Ch 13 §6.3. The security program covers DevSecOps lifecycle
  integration: requirements, design, build, run.
- **Construction §4.16–4.17 (AI-assisted development).** Anchored
  by `docs/prompt-versioning-policy.md` (slash-command and agent
  prompt changes are contract changes) and
  `docs/llm-output-verification-rubric.md` (explicit checks for
  fabricated metrics, hallucinated paths, unsupported external
  state, missing citations).

The bridge is documented in `docs/STANDARDS.md`, which lists every
standard the template references — ISO/IEC/IEEE 32675:2022, IEEE
42010, the AGENTS.md format from the Linux Foundation Agentic AI
Foundation, IEEE 2675, CycloneDX or SPDX for SBOMs, the CERT Top 10
for secure coding, and SWEBOK v4 itself. The standards register is
the source of truth for "what authority is this rule grounded in?"

## 7. Living documentation and traceability

The hardest documentation problem is not authoring; it is
preventing decay. A document written today that references a file
path or a function name is correct today and increasingly wrong
every day after.

The template's response is mechanical: a machine-readable
traceability matrix at `specs/traceability.json`, validated by a
JSON Schema at `specs/traceability.schema.json`, exercised by
`scripts/check-traceability.sh`, and enforced as a CI gate. Each
acceptance criterion in a spec maps to source files (by glob),
test files (by glob), and evidence artifacts (by exact path). The
validator confirms that each glob matches at least one real file
and each evidence artifact exists. Missing matches surface as
errors; extras surface as warnings.

A second mechanism — `scripts/check-doc-drift.sh` — greps every
relative path-like token in `docs/*.md` and `specs/**/*.md` and
verifies the path exists in the repo. Initially it warns rather
than blocks (paths churn during early development); after the
project stabilizes, the gate is hardened to block.

A third mechanism — `docs/documentation-ownership.md` — records
the RACI matrix for each living document. Solo-operator projects
do not escape this requirement; "future you returning after a
six-month break is effectively a different person" is a real
ownership gap.

A fourth mechanism — the `/sync` slash command — runs after every
PR merge to refresh local state, prune stale branches, re-run
validation on the freshly-merged default branch, walk the living
docs for drift, and write an append-only sync record under
`report/`. The sync record is the operational counterpart to a
session log: the session log captures what happened *during* a
session; the sync record captures workspace state *between*
sessions. Together they close the temporal gap that lets stale
state accumulate commit-to-commit.

## 8. AI-assisted development guardrails

SWEBOK v4 §4.16–4.17 explicitly recognizes that AI-assisted
development introduces failure modes the previous version did not
contemplate. The template's response is a small set of explicit
artifacts:

- `docs/prompt-versioning-policy.md` — slash-command and
  agent-prompt changes are contract changes, with the same review
  weight as a behavior-changing code change. A diff to
  `.claude/commands/implement.md` requires the same scrutiny as a
  diff to `src/implement_handler.py`.
- `docs/llm-output-verification-rubric.md` — explicit checks for
  the specific failure modes LLMs exhibit: fabricated metrics
  (numbers that look plausible but were never measured),
  hallucinated paths (file paths that look right but don't
  exist), unsupported external state (claims about CI status
  without a CI URL), missing citations (claims about library
  behavior without a doc link). The rubric is checked manually
  during review and informs the runtime hook's allow-list of
  tools.
- `CONSTITUTION.md §P8` — risk-class autonomy. The agent's
  permission to act without confirmation is a function of the
  task's risk class, with explicit demotion rules for security-
  relevant work. This is the constitutional anchor for the
  ask/auto/YOLO mode toggle most agentic CLIs expose.

## 9. Day-1 / Day-2 / Day-3 bring-up

A new project bootstrapped from this template follows a three-day
shakedown. The cadence is artificial — the work could be done in
an afternoon — but the rhythm forces explicit verification at each
step rather than discovering at Day 30 that a layer was never
exercised.

**Day 1 — Scaffold and customize.** Run `cookiecutter`. Customize
`CONSTITUTION.md` (project-specific principles, if any),
`DIRECTIVES.md` (project-specific directives, if any), and
`SECURITY.md` (correct disclosure email, supported version policy).
Run `make sync && make validate`. All gates pass on the empty
scaffold. Commit on a `feat/initial` branch and confirm the
runtime hook blocks an attempt to commit on `main`.

**Day 2 — First spec, first feature.** Run `/spec-bump` to create
the first ADR (`adr-0001-governance-foundation.md` ships as a seed
example; the second ADR is the first real one). Use `/plan` to
draft a feature spec, `/implement` to build it, `/test` to verify,
`/review` to inspect, and `/commit` to land it. After merge, run
`/sync` to refresh the workspace and confirm no living-doc drift.

**Day 3 — Threat model and traceability.** Use `/threat-model` to
walk the STRIDE table for the new feature. Update
`docs/THREAT_MODEL.md` if new attack surface was introduced. Add
the feature's acceptance criteria to `specs/traceability.json`.
Run `/check-traceability` to confirm clean. Run `/audit` to confirm
the full system is consistent.

By Day 4, the project is operationally healthy. By Day 30, the
project has accumulated enough evidence under `report/` to be
forensically auditable. By Day 365, the audit trail tells the
story of every decision the project made.

## 10. Why this approach

**Tested under load.** The methodology is distilled from three
projects that ran agentic workflows in production-adjacent
conditions (`sdlc_app`, `ADWS_PRO`, `govforge`). Every directive in
the register exists because a previous project's absence of that
directive caused real damage that a real human had to repair.

**Mechanically enforced.** The methodology has no advice. Every
rule has an enforcement layer — a runtime hook, a CI gate, a
governance check, or a command structure that makes the rule the
default path. Rules that cannot be enforced mechanically are
listed under `RECOMMENDED` and explicitly accepted as soft signals
rather than hard rules.

**SWEBOK-anchored.** Every architectural decision in the template
cites a SWEBOK chapter, an IEEE standard, or an industry standard
(Linux Foundation AGENTS.md, CycloneDX, CERT). Citations are
verifiable; invented authority is not.

**Solo-friendly.** The methodology scales down to one operator
without losing structural integrity. A solo operator running this
methodology is, in practice, doing the work of a five-person team
— but the *infrastructure* of governance is what makes the work
tractable, not the headcount.

**Dogfood-tested.** This template's own build follows its rules.
Every phase of the build commits on a `feat/scaffold-phase-<N>`
branch, with no `--no-verify`, no commits to `main`, no stub
markers anywhere. The methodology applies to the methodology's
own construction.

## 11. Limits and what the methodology does not do

The methodology is not a substitute for engineering judgment. The
runtime hook prevents a commit to `main`; it does not prevent a
poorly-designed feature from being shipped. The threat model
captures STRIDE rows; it does not author the mitigations. The
traceability matrix verifies file existence; it does not verify
that the implementation matches the specification's intent.

The methodology is not a security framework. It complements
SOC 2, ISO 27001, NIST SSDF, and similar frameworks; it does not
replace them. A project that requires formal security
certification still needs the certification work; this template
provides the engineering substrate that makes the certification
work tractable.

The methodology is not language-agnostic at the build-tooling
level. The runtime hook is Node.js. The Makefile assumes a Unix
shell. The Python path uses `pyproject.toml` and `pip` (with
`uv` optional); the TypeScript path uses `package.json` and
`npm`. Polyglot projects use both. Projects in other languages
(Go, Rust, Elixir) need to author their own equivalents of the
build glue, retaining the directive register and the runtime hook
structure.

## 12. What survives without the template

If the template is discarded tomorrow, what stays:

- The eight constitutional principles. They are not template-
  specific; they describe how to run a project under any
  conditions.
- The eighteen directives' structure. The specific IDs and
  statements may evolve, but the three-class register (Critical /
  Important / Recommended) and the requirement that every
  directive name its enforcement mechanism are durable.
- The five-layer model. Defense in depth applies to any system
  where the agent's output is consumed mechanically.
- The SWEBOK v4 anchor pattern. Naming the standard each artifact
  bridges to is a documentation discipline that survives the
  artifact.
- The traceability-matrix-as-code idea. The specific format
  (`traceability.json` with JSON Schema) may change; the principle
  that documentation drift must be mechanically detected is
  durable.
- The append-only evidence trail. Every project keeps a `report/`
  directory of dated, immutable artifacts. Whether the artifacts
  are markdown, JSON, or screenshots is incidental.

Those six items are the methodology. The template is one
realization. A different realization in a different language with
different tooling can carry the same methodology without sharing a
single line of code with this template.

---

*Authored 2026-05-01. The directive register may evolve; the
constitutional principles are stable.*
