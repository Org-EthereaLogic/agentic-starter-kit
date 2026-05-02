# External Template Research — Findings & Gap Analysis

> **Precedence note:** `EXTENSIONS_DECISIONS.md` supersedes specific
> portions of this file. In particular, Decision 2 in that file
> rejects the symlink mechanic discussed in §3.1 below; Decision 3
> tiers the size cap. Read `EXTENSIONS_DECISIONS.md` first when
> these subjects come up. Other findings in this document remain
> authoritative.
>
> **Purpose:** comparative analysis of popular GitHub templates,
> agentic coding starter kits, spec-driven methodologies, and OSS
> supply-chain standards versus the current `agentic-starter-kit`
> build. Each finding includes a verdict on whether it gets pulled
> into our template and where.
>
> **Author note:** this file is reference material for the IDE
> agent. When extending the template per `IDE_PROMPT_PHASE_12.md`,
> treat the verdicts in this document as authoritative except
> where `EXTENSIONS_DECISIONS.md` overrides.
>
> **Created:** 2026-05-01.

---

## 1. Templates surveyed

| Template | Stars / Posture | Primary Pattern Borrowed |
|---|---|---|
| `cookiecutter-uv` (osprey-oss / fpgmaas) | ~1.2k stars, modern Python | uv-first, ruff + mypy + deptry, MkDocs Material, src-or-flat layout |
| `audreyfeldroy/cookiecutter-pypackage` | classic Python | SHA-pinned actions + minimal permissions baseline |
| `cookiecutter-uv-hypermodern-python` (bosd) | comprehensive Python | Nox as cross-version task runner; pre-commit + uv integration |
| `wyattferguson/pattern` | opinionated Python UV | GitHub issue/PR/feature templates; CITATION.cff; CODE_OF_CONDUCT.md |
| `tiangolo/full-stack-fastapi-postgresql` | full-stack | Docker-first; auto HTTPS via Traefik |
| `github/spec-kit` | 39.3k stars, GitHub-backed | `constitution.md` + `/specify` `/plan` `/tasks` flow; presets |
| `OpenSpec` (~4.1k stars) | brownfield-first | `openspec/changes/<id>/` delta-only spec proposals; AGENTS.md fallback |
| `BMAD-METHOD` | comprehensive multi-agent | Named personas (Mary, Preston, Winston, Sally, Simon, Devon, Quinn); file-based handoff |
| `TheDecipherist/claude-code-mastery-project-starter-kit` | full-featured Claude Code | `/new-project`, `/convert-project-to-starter-kit` (non-destructive merge), Live AI Monitor (`/what-is-my-ai-doing`), parallel worktrees, MDD workflow |
| `peterkrueck/Claude-Code-Development-Kit` | beginner-to-intermediate | `/prime`, `/update-docs`, security scanner blocking secrets through MCP, deny list, `/review-work` parallel sub-agents |
| `pedrohcgs/claude-code-my-workflow` | academic focus | Critic + fixer adversarial loop until APPROVED; PreCompact hook saves snapshot before auto-compression; quality scoring (0–100) |
| `serpro69/claude-toolbox` | multi-lang | 10-skill pipeline (`/design` → `/review-design` → `/implement` → `/review-code` → `/test` → `/document`); Capy for cross-session memory |
| `wshobson/agents` | comprehensive marketplace | 184 agents, 150 skills, 98 commands; evaluation layers (static, LLM judge, Monte Carlo); quality badges (Platinum/Gold/Silver/Bronze); anti-pattern detection |
| `davila7/claude-code-templates` | a-la-carte | CLI installs individual components |
| `alirezarezvani/claude-skills` | cross-tool skills | 232+ skills working across 11 platforms; `scripts/convert.sh` to translate skill formats |
| `GoogleCloudPlatform/agent-starter-pack` | GCP production agents | One-command project gen, Terraform infra, Cloud Build / GitHub Actions CI, monitoring + observability |

---

## 2. Standards & ecosystems referenced

| Standard / Ecosystem | What it is | Verdict |
|---|---|---|
| **AGENTS.md** (Linux Foundation Agentic AI Foundation) | Cross-tool agent instruction format; 6 core areas (commands, testing, project structure, code style, git workflow, boundaries); supports `AGENTS.override.md` nesting; Codex caps at 32 KiB | **Adopt as primary**; CLAUDE.md and GEMINI.md become derived artifacts via sync-script + drift-check (see EXTENSIONS_DECISIONS.md Decision 2 — supersedes the symlink approach originally proposed) |
| **SKILL.md** (Linux Foundation) | Portable directory format: `SKILL.md` + `scripts/` + `references/` + `assets/`; progressive disclosure via frontmatter | **Adopt** as `.claude/skills/` pattern; ship 2 seed skills |
| **OpenSSF Scorecard** | 18+ automated security checks (branch protection, code review, dependency mgmt, fuzzing, etc.); GitHub Action | **Adopt** as CI job; aim for ≥7/10 baseline |
| **OpenSSF Best Practices Badge** | Passing / Silver / Gold security & sustainment criteria | **Document** opt-in path; not auto-enrolled |
| **SLSA** (Supply-chain Levels for Software Artifacts) | L1–L4 build provenance; `slsa-github-generator` produces verifiable provenance | **Adopt** L3 baseline for release artifacts (conditional on `include_sbom`) |
| **SECURITY-INSIGHTS.yml** | Machine-readable security info per OpenSSF | **Adopt** as required file in govern-check |
| **OSV.dev** | Vulnerability database, alternative to Snyk for scanning | **Document** as Snyk-alternative; don't add by default |
| **Sigstore** | Keyless signing for artifacts; `cosign` CLI | **Adopt** for release signing (conditional on `include_sigstore`) |
| **OSS-Fuzz** | Fuzzing service for OSS projects | **Document** opt-in; don't auto-enroll |
| **Conventional Commits** | `<type>(<scope>): <description>` format | Already adopted as IMP-002 |
| **release-please** (Google) | GitHub Action that creates a Release PR; merging publishes | **Adopt** as default release tool; conditional |
| **semantic-release** | Fully-automated alternative to release-please | **Document** as alternative |
| **commitlint** + **commitizen** | Conventional-commit linting and authoring helpers | **Adopt commitlint** in pre-commit; commitizen optional |
| **MkDocs Material** | Python docs site generator | **Adopt** for Python path; conditional on `include_docs_site` |
| **VitePress** | TypeScript docs site generator | **Adopt** for TS path; conditional on `include_docs_site` |
| **devcontainer.json** | Reproducible dev environment for VS Code / Codespaces | **Adopt** as required; major reproducibility win |
| **Contributor Covenant 2.1** | Code of conduct standard | **Adopt** as `CODE_OF_CONDUCT.md` |
| **Keep a Changelog** | Format for `CHANGELOG.md` | **Adopt** for the templated `CHANGELOG.md` |
| **CITATION.cff** | Citation File Format (academic) | **Optional**; conditional on `include_citation` |

---

## 3. Pattern-by-pattern findings

### 3.1 AGENTS.md as primary, not just one of three

**Finding.** Across the surveyed templates, AGENTS.md (governed by the
Linux Foundation Agentic AI Foundation) has won as the cross-tool
standard. OpenAI's own Codex repository ships 88 AGENTS.md files
across its directory tree. As of April 2026, Claude Code does not
natively support AGENTS.md — the standard workaround is a symlink:
`ln -s AGENTS.md CLAUDE.md`. A Princeton study found AGENTS.md
presence improved coding-task success rates; LLM-generated
AGENTS.md files (longer, generic) reduced success by 2% and
increased cost by 23%, suggesting **shorter, hand-written files
perform better**.

**Current state.** The template ships CLAUDE.md, AGENTS.md, and
GEMINI.md as three separate files, treating them as parallel.

**Action.** Demote CLAUDE.md and GEMINI.md to **derived artifacts**
generated from AGENTS.md by `scripts/sync-agent-files.sh`, with
drift detection via pre-commit hook and `make governance-check`.
This supersedes the symlink approach originally proposed — see
`EXTENSIONS_DECISIONS.md` Decision 2 for the rationale (Windows
`core.symlinks=false` and Codespaces edge cases). Add
`AGENTS.override.md` documentation for nested overrides. Keep
each file under 16 KiB (soft target; hard cap 24 KiB) per
`EXTENSIONS_DECISIONS.md` Decision 3 to stay below Codex's 32 KiB
cap and respect the Princeton finding. Add a "boundaries" section
using the three-tier pattern (always do / ask first / never do)
found by the GitHub blog analysis of 2,500+ AGENTS.md files to be
the highest-correlation success pattern.

**Lands in.** GAP-EXT-001.

### 3.2 Skills system (SKILL.md)

**Finding.** Skills are now a portable, progressive-disclosure format
for capability packaging. A skill is a directory containing
`SKILL.md` + optional `scripts/` + `references/` + `assets/`. When
the agent starts, it reads only the YAML frontmatter (name +
description) for every skill. The full body loads only when the task
matches. This keeps the always-on context budget lean. Multi-tool:
works in Claude, Codex, Gemini CLI, Cursor.

**Current state.** No skills directory.

**Action.** Add `.claude/skills/` (mirrored to `.agents/skills/` or
synced via the same pattern as AGENTS.md → CLAUDE.md). Ship two
seed skills:

- `governance-audit` — packages the audit-step prose and the
  `make audit` wrapper
- `spec-bump` — packages the spec-versioning workflow

Document the pattern for adding new skills.

**Lands in.** GAP-EXT-002.

### 3.3 OpenSSF supply-chain security stack

**Finding.** Three OpenSSF projects compose into a defensible
supply-chain posture: **Scorecard** (development-practice quality),
**SLSA** (build-process integrity), and **SBOM** (component
visibility). Scorecard runs 18+ checks including branch protection,
code review, fuzzing, signed releases, and unpinned dependencies.
SLSA L3 produces verifiable build provenance via
`slsa-framework/slsa-github-generator`. SECURITY-INSIGHTS.yml is the
machine-readable security info file that ties them together.

**Current state.** SBOM is in the gap register (GAP-022) but
Scorecard, SLSA, and SECURITY-INSIGHTS.yml are not.

**Action.** Add the Scorecard GitHub Action workflow (target ≥7/10
baseline). Add SLSA L3 provenance generation conditional on
`include_sbom=yes`. Add SECURITY-INSIGHTS.yml as a required file in
governance-check. Document the OpenSSF Best Practices Badge opt-in
process (don't auto-enroll).

**Lands in.** GAP-EXT-003 through GAP-EXT-006.

### 3.4 Devcontainer / Codespaces support

**Finding.** Modern templates (cookiecutter-uv, the Microsoft
`vscode-remote-try-*` family, all Google template variants) ship
`.devcontainer/devcontainer.json`. This makes the project openable
in a Codespace with one click and gives every contributor the same
toolchain via a `postCreateCommand` (typically running
`make sync && pre-commit install`). Features
(`ghcr.io/devcontainers/features/*`) install language toolchains,
git, gh CLI, etc.

**Current state.** No devcontainer.

**Action.** Add `.devcontainer/devcontainer.json` (and a `Dockerfile`
when needed) shipping uv, Node, gh CLI, pre-commit. Wire
`postCreateCommand` to `make sync && pre-commit install`. Pre-install
a curated VS Code extensions list (Python, ESLint, GitLens,
markdownlint, etc., conditional on language path).

**Lands in.** GAP-EXT-007.

### 3.5 Release automation: release-please

**Finding.** Two leading approaches:

- **release-please** (Google) — creates and maintains a single
  "Release PR" that aggregates conventional commits since the last
  release; merging the PR publishes. Fully GitHub-native.
- **semantic-release** — fully autonomous; tags + publishes on
  every relevant push to a release branch. More magic, less control.

For our risk profile (solo operator, manual gatekeeping), **release-
please is the better default** because the human merge of the
Release PR is the explicit "ship this version" decision.

**Current state.** Conventional commits are required (IMP-002) but
no release-automation tooling ships with the template.

**Action.** Add `.github/workflows/release-please.yml` and
`release-please-config.json` (conditional on `include_release_automation=yes`).
Document semantic-release as an alternative.

**Lands in.** GAP-EXT-008.

### 3.6 Documentation site (MkDocs Material / VitePress)

**Finding.** Modern Python templates ship MkDocs Material for docs
hosted on GitHub Pages. TypeScript templates use VitePress. This
turns `docs/` from a folder of markdown files into a navigable site
with search, theme, and version selectors.

**Current state.** `docs/` is a markdown folder. No site generator.

**Action.** Add MkDocs Material config for Python path and VitePress
config for TS path, conditional on a new `include_docs_site=yes`
cookiecutter option. GitHub Pages auto-deploy workflow on push to
default branch.

**Lands in.** GAP-EXT-009.

### 3.7 Repository hygiene files

**Finding.** Top-tier OSS templates ship a consistent set of
community files:

- `CHANGELOG.md` (Keep a Changelog format) — required for
  release-please anyway
- `CODE_OF_CONDUCT.md` (Contributor Covenant 2.1) — community norm
- `.github/ISSUE_TEMPLATE/bug_report.yml`,
  `feature_request.yml`, `support.yml` — issue forms
- `.github/FUNDING.yml` — optional sponsorship config
- `CITATION.cff` — academic citation, optional
- `MAINTAINERS.md` — ownership / RACI

**Current state.** Template ships `CONTRIBUTING.md`, `LICENSE`,
`SECURITY.md`, `.github/PULL_REQUEST_TEMPLATE.md`. Missing the rest.

**Action.** Add the missing files. `CHANGELOG.md` and
`CODE_OF_CONDUCT.md` are unconditional. The others are conditional.

**Lands in.** GAP-EXT-010 through GAP-EXT-013.

### 3.8 commitlint as pre-commit hook

**Finding.** Conventional-commit conformance can be locally enforced
via `commitlint` in a `commit-msg` pre-commit hook, blocking
non-conforming messages before they hit the remote. Pairs with
`commitizen` (CLI helper) for authoring.

**Current state.** IMP-002 says use conventional commits but doesn't
mechanically enforce.

**Action.** Add `@commitlint/cli` + `@commitlint/config-conventional`
to `.pre-commit-config.yaml` (commit-msg stage). Document
commitizen as optional authoring helper.

**Lands in.** GAP-EXT-014.

### 3.9 deptry (unused dependency detection)

**Finding.** `deptry` is a lightweight tool that detects undeclared
dependencies, unused dependencies, and dependency misuse in Python
projects. Standard in cookiecutter-uv. Catches a real class of bug
(transitive dep being relied on) that ruff/mypy don't.

**Current state.** Python path uses ruff + mypy. No dependency
hygiene tool.

**Action.** Add `deptry` to dev dependencies and to `make validate`
on Python path.

**Lands in.** GAP-EXT-015.

### 3.10 Spec-driven development integration

**Finding.** Three SDD frameworks have matured:

- **Spec Kit** (39k+ stars) — `/specify`, `/plan`, `/tasks`,
  constitution-anchored, GitHub-native
- **OpenSpec** — brownfield-first; `openspec/changes/<id>/`
  delta-only proposals
- **BMAD-METHOD** — multi-agent personas (Mary/Preston/Winston/etc.)
  with file-based handoff (`docs/requirements.md` →
  `docs/architecture.md` → ...)

Our `specs/` directory + `/plan` + `/implement` is closest in shape
to Spec Kit but doesn't formally integrate any of these.

**Current state.** Custom spec model.

**Action.** **Don't fork to a new framework.** Instead:

1. Add **OpenSpec-style change proposals** as
   `specs/changes/<change-id>/` for brownfield evolution (lighter
   than full ADRs).
2. Document compatibility with Spec Kit's `constitution.md` (our
   `CONSTITUTION.md` is functionally identical).
3. Add a `BMAD-COMPATIBILITY.md` doc explaining how our agents map
   onto BMAD personas for users coming from that framework.

**Lands in.** GAP-EXT-016.

### 3.11 Adversarial review pattern

**Finding.** `pedrohcgs/claude-code-my-workflow` introduces a
**critic + fixer adversarial loop**: two agents work in opposition,
the critic produces harsh findings, the fixer implements exactly
what the critic found, looping until the critic says APPROVED (or
5 rounds max). Catches errors single-pass review misses.

`peterkrueck/Claude-Code-Development-Kit`'s `/review-work` runs
parallel sub-agents (Bug Hunter + Rules Auditor) on the
uncommitted diff.

**Current state.** Single `/review` agent.

**Action.** Add `/adversarial-review` command that runs the
`security-reviewer` and `lead-software-engineer` agents in
opposition on a diff or PR, looping until the security-reviewer
returns APPROVED.

**Lands in.** GAP-EXT-017.

### 3.12 Live AI monitoring

**Finding.** Decipherist's `/what-is-my-ai-doing` provides real-time
visibility into tool calls, token use, cost, and rule violations.
This is operationally important — without it, "the agent did
something" is opaque.

**Current state.** No monitor.

**Action.** Add a `PostToolUse` logging hook that appends to
`.claude/agent-memory/tool-trace.jsonl` (already gitignored). Add a
`make monitor` Makefile target that tails the trace. Don't try to
build a full UI — JSON Lines + `jq` is enough.

**Lands in.** GAP-EXT-018.

### 3.13 PreCompact context-snapshot hook

**Finding.** When Claude Code's auto-compression triggers, plans
and decisions can be lost. `pedrohcgs/claude-code-my-workflow`
adds a `PreCompact` hook that saves a context snapshot before
compression.

**Current state.** No PreCompact hook.

**Action.** Add `.claude/hooks/pre-compact.js` that writes the
current session state (last N user messages, current branch, open
todos) to `report/<UTC-timestamp>-pre-compact-snapshot.md`.
Append-only per IMP-001.

**Lands in.** GAP-EXT-019.

### 3.14 MCP server documentation

**Finding.** `serpro69/claude-toolbox` ships MCP wiring (Serena LSP
integration, Capy memory, etc.). `peterkrueck/Claude-Code-Development-Kit`
has a security scanner for MCP plugins. Our template is silent on
MCP.

**Current state.** No MCP guidance.

**Action.** Add `docs/mcp-servers.md` documenting recommended MCP
servers (filesystem, git, semgrep, sequential-thinking) and the
security-scanner pattern for vetting third-party MCP servers.
Don't auto-install MCP servers — that's user choice.

**Lands in.** GAP-EXT-020.

### 3.15 Agent / command quality evaluation

**Finding.** `wshobson/agents` runs three evaluation layers on
its 184 agents and 150 skills:

1. **Static analysis** (instant) — frontmatter linting, length
   checks, broken cross-references
2. **LLM judge** (semantic) — quality grading
3. **Monte Carlo simulation** (statistical) — does the trigger
   actually fire when expected

Plus anti-pattern detection: OVER_CONSTRAINED, EMPTY_DESCRIPTION,
MISSING_TRIGGER, BLOATED_SKILL, ORPHAN_REFERENCE, DEAD_CROSS_REF.

**Current state.** No agent/command linting.

**Action.** Add `scripts/lint-agents.sh` that performs the static-
analysis layer (frontmatter present, descriptions non-empty,
description length ≤200 chars, no stub markers, no orphan
cross-references). Add to `make validate`. Don't ship the LLM
judge or Monte Carlo layers — those are heavier than the project
warrants right now.

**Lands in.** GAP-EXT-021.

### 3.16 OpenSpec-style brownfield change proposals

**Finding.** OpenSpec's value proposition is for evolving existing
codebases incrementally rather than authoring full ADRs for every
change. Pattern: `openspec/changes/<change-id>/` with a delta-only
spec, AI-iterated until consensus, archived to `openspec/specs/`
on merge.

**Current state.** Full ADR/RFC required for changes.

**Action.** Already covered in 3.10 above; details: introduce
`specs/changes/` as a lighter-weight alternative for incremental
modifications. Each change-proposal has: `proposal.md` (what's
changing), `delta.md` (against current spec), `acceptance.md`
(testable criteria). Archive to `specs/deep_specs/changes-archive/`
on merge.

**Lands in.** GAP-EXT-016 (combined).

### 3.17 BMAD persona mapping

**Finding.** BMAD's named personas (Mary Analyst, Preston PM,
Winston Architect, Sally PO, Simon SM, Devon Dev, Quinn QA)
provide a mental model for delegating to specialized agents.
Our agents are functionally similar but un-named.

**Current state.** Functional agent names.

**Action.** Don't rename our agents — function-named is more
self-documenting than persona-named. Instead add
`docs/bmad-mapping.md` showing how a BMAD user can find the
equivalent agent in our template.

**Lands in.** GAP-EXT-022.

### 3.18 Just / justfile alternative to Make

**Finding.** Modern projects increasingly prefer `just` over `make`
for task running — cleaner syntax, no tab-vs-space issues, runs the
same on macOS / Linux / Windows.

**Current state.** `Makefile` is canonical.

**Action.** Add `just` as an alternative path conditional on a new
`task_runner` cookiecutter option (default `make`, alternative
`just`). Both ship identical targets. Don't ship both —
the post-gen hook removes the unused one.

**Lands in.** GAP-EXT-023.

### 3.19 Onboarding automation

**Finding.** `make sync` is good but assumes the contributor has
the right global tools. Modern templates ship a `bootstrap.sh`
that installs uv, Node, pre-commit, gh CLI, etc., or document the
exact prerequisites in a `/start` slash command.

**Current state.** `/start` slash command planned per Phase 9.

**Action.** Strengthen `/start` to detect missing tooling and
print install instructions per OS. Add a one-line `bootstrap.sh`
that runs `make sync` after installing what's missing. Document
both in the README.

**Lands in.** GAP-EXT-024.

---

## 4. Anti-patterns (things we will not adopt)

These appear in surveyed templates but are explicitly rejected for
our context:

| Anti-pattern | Why we reject |
|---|---|
| **LLM-generated AGENTS.md files** | Princeton study: -2% success, +23% cost. Our AGENTS.md is hand-authored and stays under 16 KiB (soft target). |
| **Auto-enroll in OpenSSF Best Practices Badge** | Voluntary commitment; better as documentation pointing the user at the opt-in path. |
| **All-three SDD frameworks at once** (Spec Kit + OpenSpec + BMAD) | Compatibility docs are cheap; framework collisions are expensive. We ship our model and document interop. |
| **Plugin marketplace approach** | We're a single template; not building a registry. |
| **Auto-installed MCP servers** | User choice. Document the recommended set; install nothing automatically. |
| **Renaming agents to BMAD personas** | Function names self-document better than person names for solo operators. |
| **Live-spec automation that writes back to specs** | Drift detection (read-only) is safe; auto-spec-update is not. Specs are versioned governance, not generated artifacts. |
| **`semantic-release` over `release-please` as default** | Fully-automated publishing removes the human gatekeeper that solo operators need. |
| **Persistent-identity sub-agents with custom tool grants** | Adds complexity without clear ROI for our scale. Reconsider in v2. |
| **Symlinking CLAUDE.md → AGENTS.md** | Cross-platform fragility (Windows, Codespaces). Replaced by sync-script + drift-check per `EXTENSIONS_DECISIONS.md` Decision 2. |

---

## 5. Anti-pattern detection rules adopted

From `wshobson/agents`, we adopt these as `scripts/lint-agents.sh`
checks:

| Anti-pattern | Detection rule |
|---|---|
| `EMPTY_DESCRIPTION` | YAML frontmatter `description` field is empty or `<2 words` |
| `MISSING_TRIGGER` | Slash-command file has no `description` or `argument-hint` field |
| `BLOATED_SKILL` | SKILL.md body exceeds 6 KiB (progressive disclosure violated) |
| `ORPHAN_REFERENCE` | File path mentioned in spec/agent does not exist in repo |
| `DEAD_CROSS_REF` | Markdown link target file does not exist |
| `OVER_CONSTRAINED` | Agent prompt has >10 "MUST NOT" rules — likely over-specified |
| `STUB_MARKER` | Already covered by `marker-scan.sh` (CRIT-001) |
| `AGENTS_MD_OVERSIZE_WARN` | `AGENTS.md` ≥16 KiB (warn, per `EXTENSIONS_DECISIONS.md` Decision 3) |
| `AGENTS_MD_OVERSIZE_FAIL` | `AGENTS.md` ≥24 KiB (fail) |

---

## 6. Verdicts summary

24 GAP-EXT entries land in the gap register extension. They organize
into:

- **Tier 1 — high impact, low effort (do first):**
  GAP-EXT-001 (AGENTS.md primary), GAP-EXT-003 through GAP-EXT-006
  (OpenSSF stack + SECURITY-INSIGHTS.yml), GAP-EXT-007 (devcontainer),
  GAP-EXT-010 / 011 (CHANGELOG, CODE_OF_CONDUCT), GAP-EXT-012 (issue
  templates), GAP-EXT-014 (commitlint), GAP-EXT-021 (lint-agents.sh).

- **Tier 2 — high impact, moderate effort:**
  GAP-EXT-002 (skills), GAP-EXT-008 (release-please), GAP-EXT-009
  (docs site), GAP-EXT-015 (deptry), GAP-EXT-016 (OpenSpec changes
  pattern), GAP-EXT-017 (adversarial review), GAP-EXT-019
  (PreCompact hook), GAP-EXT-024 (onboarding).

- **Tier 3 — strategic / niche:**
  GAP-EXT-013 (CITATION.cff, FUNDING.yml), GAP-EXT-018 (live monitor),
  GAP-EXT-020 (MCP docs), GAP-EXT-022 (BMAD mapping), GAP-EXT-023
  (just alternative).

The IDE-prompt in `IDE_PROMPT_PHASE_12.md` runs all three tiers
in order.
