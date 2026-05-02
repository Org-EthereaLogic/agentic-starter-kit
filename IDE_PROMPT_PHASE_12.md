# IDE Prompt — Agentic Starter Kit, Extensions Build (Phases 12–15)

> **How to use this:** open VS Code Insiders, navigate to
> `/Users/etherealogic-2/Dev/agentic-starter-kit`, start a new
> Claude Code session in this directory, and paste the
> `## PROMPT (paste from here)` section below as your first message.
>
> **Prerequisite:** Phases 0–11 from `IDE_PROMPT.md` must already be
> complete. The base template scaffold is required before Phases
> 12–15 can run.
>
> The agent has full filesystem access in this directory and read
> access to the source projects (`govforge`, `sdlc_app`, `ADWS_PRO`).
> External research has already been done; the findings are in
> `RESEARCH_FINDINGS.md` and the gap inventory is in
> `SWEBOK_GAP_REGISTER_EXTENSIONS.md`.

---

## PROMPT (paste from here)

You are extending the `agentic-starter-kit` template with **24 new
gaps** identified through an external-template research pass
(popular GitHub templates, OpenSSF supply-chain standards, the
agentic-tooling ecosystem). The base template (Phases 0–11) is
already complete. Your job is Phases 12–15.

### Step 1 — Read the planning files in order

Before authoring anything, read all five in this order:

1. `BRIEFING.md` — mission, the five layers, eight constitutional
   principles, eighteen directives, authorial style rules. **The
   style rules from §6 apply to every file you write in this
   extension.**
2. `RESEARCH_FINDINGS.md` — what was researched, what we adopt,
   what we reject. Verdicts in this file are authoritative.
3. `SWEBOK_GAP_REGISTER.md` — the original 53 gaps. Treat as
   reference; do not modify rows here.
4. `SWEBOK_GAP_REGISTER_EXTENSIONS.md` — the **24 new gaps**
   (GAP-EXT-001 through GAP-EXT-024) you are landing in this
   build. Use this as your master checklist.
5. `BUILD_PLAN.md` — original phasing for Phases 0–11 (already
   done). Reference only.

After reading, summarize back to me in one short paragraph what
you understand the extension build to be and which phase boundaries
you'll commit on. Do not start authoring until I confirm.

### Step 2 — Phase 12: Cross-tool standardization + community files

Land these gaps as one phase (one feat branch, one PR):

**GAP-EXT-001 — AGENTS.md as primary cross-tool standard.**

- Rewrite `{{cookiecutter.project_slug}}/AGENTS.md` to follow the
  Linux Foundation Agentic AI Foundation specification: six core
  sections (Commands, Testing, Project Structure, Code Style,
  Git Workflow, Boundaries). The Boundaries section uses the
  three-tier pattern: **always do**, **ask first**, **never do**.
  Cite our directives by ID where they apply.
- Keep AGENTS.md under **16 KiB**. The Princeton study shows
  shorter agent-instruction files outperform long ones; Codex
  caps at 32 KiB. Stay well below the cap.
- Delete the standalone CLAUDE.md and GEMINI.md content. Replace
  with symlinks. Update `hooks/post_gen_project.py` to:
  ```python
  os.symlink("AGENTS.md", "CLAUDE.md")
  os.symlink("AGENTS.md", "GEMINI.md")
  ```
  Symlinks must be created relatively (so the project remains
  portable) and after the templated AGENTS.md is rendered.
- Add `AGENTS.override.md` documentation in
  `docs/agent-runtimes.md` for nested-directory overrides. Cite
  OpenAI's Codex repository (88 AGENTS.md files) as the precedent.
- Update `scripts/check-governance.sh` to verify CLAUDE.md is a
  symlink that resolves to AGENTS.md, and that AGENTS.md size is
  ≤16 KiB.

**GAP-EXT-002 — Skills system.**

- Create `{{cookiecutter.project_slug}}/.claude/skills/` directory.
- Author 2 seed skills:
  - `governance-audit/SKILL.md` — packages the audit prose so
    `/audit` becomes more progressive-disclosure friendly. Includes
    `scripts/audit.sh` referencing the existing audit logic.
  - `spec-bump/SKILL.md` — packages the spec-versioning workflow.
- Each SKILL.md uses YAML frontmatter (`name`, `description`).
  Body kept under **6 KiB** (BLOATED_SKILL anti-pattern threshold).
- Add `docs/agent-skills-pattern.md` documenting how to add new
  skills.
- Mirror to `.agents/skills/` via post-gen symlink for cross-tool
  compatibility.

**GAP-EXT-010, 011, 012, 013 — Community files.**

- `{{cookiecutter.project_slug}}/CHANGELOG.md` — Keep a Changelog
  format; seed with one `Unreleased` section.
- `{{cookiecutter.project_slug}}/CODE_OF_CONDUCT.md` — Contributor
  Covenant 2.1 verbatim with project name parameterized.
- `.github/ISSUE_TEMPLATE/bug_report.yml`, `feature_request.yml`,
  `support.yml`, `config.yml` — GitHub issue forms (YAML).
- `{{cookiecutter.project_slug}}/MAINTAINERS.md` — seed with the
  cookiecutter author info; document the RACI pattern.
- Conditional: `CITATION.cff` (if `include_citation=yes`),
  `.github/FUNDING.yml` (if `include_funding=yes`).
- Update `cookiecutter.json` with the new variables.
- Update `hooks/post_gen_project.py` to remove the conditional
  files when their option is `no`.
- Update `scripts/check-governance.sh` to require CHANGELOG.md,
  CODE_OF_CONDUCT.md, SECURITY-INSIGHTS.yml (next phase),
  MAINTAINERS.md.

**Phase 12 gate:**
- All listed files render without Jinja2 errors.
- Symlinks resolve correctly post-instantiation.
- AGENTS.md ≤16 KiB.
- `make governance-check` passes on the instantiated project.

Commit on branch `feat/scaffold-phase-12`. Update
`SWEBOK_GAP_REGISTER_EXTENSIONS.md` Status cells. Open PR.

### Step 3 — Phase 13: Supply-chain security stack

**GAP-EXT-003 — OpenSSF Scorecard.**

- Add `.github/workflows/scorecard.yml` per the official OpenSSF
  template. SHA-pinned actions per IMP-006. Schedule weekly + on
  push to default branch. Upload SARIF to code-scanning.
- Add `docs/security/scorecard-policy.md` documenting the ≥7/10
  baseline target, the checks that matter most for our posture
  (Branch-Protection, Code-Review, Pinned-Dependencies,
  Token-Permissions, Signed-Releases), and how to read results.

**GAP-EXT-004 — SLSA L3 build provenance.**

- Conditional on `include_slsa=yes` (new cookiecutter variable).
- Add `.github/workflows/slsa-provenance.yml` invoking
  `slsa-framework/slsa-github-generator` (pinned by SHA).
- Add `docs/security/slsa-policy.md`.
- Couple to `release-please` workflow so provenance generates on
  release publish.

**GAP-EXT-005 — SECURITY-INSIGHTS.yml.**

- `{{cookiecutter.project_slug}}/SECURITY-INSIGHTS.yml` per the
  OpenSSF schema. Reference the existing SECURITY.md as the
  policy URL. Include `vulnerability_reporting`, `security_contact`,
  `dependencies`, `vulnerability-disclosure`.
- Update `scripts/check-governance.sh` to require it.

**GAP-EXT-006 — OpenSSF Best Practices Badge.**

- Add `docs/security/openssf-badge-path.md` documenting the opt-in
  process (passing → silver → gold). Include the criteria checklist.
- Cross-reference from `docs/cert-top-10-compliance.md`.
- Do **not** auto-enroll. The badge requires self-attestation;
  that's a project-owner decision.

**Phase 13 gate:**
- `.github/workflows/scorecard.yml` parses cleanly (use `actionlint`
  if available, else verify manually).
- `make governance-check` passes with new SECURITY-INSIGHTS.yml
  requirement.
- Smoke test: trigger the Scorecard workflow on a sample instantiated
  repo (or skip if test repo creation is out of scope) and confirm
  it runs without errors.

Commit on branch `feat/scaffold-phase-13`. Update register. PR.

### Step 4 — Phase 14: Reproducible env + release + docs site + Python hygiene

**GAP-EXT-007 — Devcontainer.**

- `{{cookiecutter.project_slug}}/.devcontainer/devcontainer.json`
  with:
  - `image`: `mcr.microsoft.com/devcontainers/base:ubuntu` or
    language-specific image conditional on `primary_language`.
  - `features`: uv, Node 20+, gh CLI, pre-commit (using
    `ghcr.io/devcontainers/features/*`).
  - `postCreateCommand`: `make sync && pre-commit install`.
  - `customizations.vscode.extensions`: curated list (Python,
    Pylance, ESLint, GitLens, markdownlint, mypy-type-checker,
    ms-azuretools.vscode-docker, ms-vscode.makefile-tools).
  - `forwardPorts`: leave empty by default.
- Add `docs/codespaces-and-devcontainers.md` explaining usage.

**GAP-EXT-008 — release-please.**

- Conditional on `include_release_automation=yes` (new variable;
  default `yes`).
- `.github/workflows/release-please.yml`, SHA-pinned.
- `release-please-config.json` configured for the project's
  language path (release-type `python` or `node`).
- `release-please-manifest.json` seeded at `0.1.0`.
- `docs/release-process.md` documenting the Release-PR pattern.

**GAP-EXT-009 — Documentation site.**

- Conditional on `include_docs_site=yes` (new variable;
  default `yes`).
- Python path: `mkdocs.yml` + Material theme + `docs/index.md`.
- TS path: `.vitepress/config.ts` + `docs/index.md`.
- `.github/workflows/docs-deploy.yml` deploying to GitHub Pages on
  push to default branch.

**GAP-EXT-014 — commitlint.**

- Add `commitlint.config.cjs` at repo root with
  `@commitlint/config-conventional`.
- Add to `.pre-commit-config.yaml` as a `commit-msg` stage hook.
  Use `alessandrojcm/commitlint-pre-commit-hook` or equivalent
  pinned by version.
- Document `commitizen` as optional in CONTRIBUTING.md.

**GAP-EXT-015 — deptry.**

- Python / polyglot only. Add `deptry` to dev dependency group in
  `pyproject.toml`.
- `Makefile`: add `deptry` target. Add to `make validate`.
- Configure deptry in `pyproject.toml` `[tool.deptry]` section
  (ignore the typical false positives for this project profile).

**Phase 14 gate:**
- Devcontainer config valid (parse with `jq`).
- release-please-config.json valid (parse with `jq`).
- mkdocs.yml or vitepress config parses.
- pre-commit run --all-files succeeds with new commitlint hook.
- `make validate` passes including new `deptry` step on Python path.

Commit on branch `feat/scaffold-phase-14`. Update register. PR.

### Step 5 — Phase 15: Workflow patterns + quality gate + polish

**GAP-EXT-016 — OpenSpec-style brownfield change proposals + SDD compatibility docs.**

- Create `{{cookiecutter.project_slug}}/specs/changes/README.md`
  documenting the pattern.
- Create `specs/changes/change-template/proposal.md`,
  `delta.md`, `acceptance.md` as a template trio.
- Update `scripts/check-traceability.sh` to walk
  `specs/changes/`.
- Add `docs/sdd-frameworks-compatibility.md` covering interop
  with Spec Kit, OpenSpec, BMAD-METHOD.

**GAP-EXT-022 — BMAD persona mapping.**

- `docs/bmad-mapping.md` showing how a BMAD user finds the
  equivalent agent in our template (Mary Analyst → ?, Preston PM →
  ?, Winston Architect → ?, Sally PO → ?, Simon SM → ?, Devon Dev
  → `lead-software-engineer`, Quinn QA → `test-automator`).

**GAP-EXT-017 — Adversarial review command.**

- `{{cookiecutter.project_slug}}/.claude/commands/adversarial-review.md`
- Workflow: invokes `security-reviewer` then
  `lead-software-engineer` in opposition; loops until APPROVED or
  5 rounds; appends round transcripts to
  `report/<UTC-timestamp>-adversarial-review-<target>.md`
  (append-only per IMP-001).

**GAP-EXT-018 — Live AI monitoring.**

- `{{cookiecutter.project_slug}}/.claude/hooks/post-tool-use.js` —
  appends `{tool, args_redacted, ts, exit, cost_estimate}` lines to
  `.claude/agent-memory/tool-trace.jsonl`. The `agent-memory/` dir
  is already gitignored.
- `Makefile`: `make monitor` tails the trace through `jq`.
- Update `.claude/settings.json` to register `PostToolUse`.

**GAP-EXT-019 — PreCompact context-snapshot hook.**

- `{{cookiecutter.project_slug}}/.claude/hooks/pre-compact.js` —
  writes a snapshot to
  `report/<UTC-timestamp>-pre-compact-snapshot.md`
  (append-only per IMP-001). Includes: current branch, last 10
  user-message summaries (first 200 chars each), open todos.
- Update `.claude/settings.json` to register `PreCompact`.

**GAP-EXT-020 — MCP server documentation.**

- `docs/mcp-servers.md` documenting recommended MCP servers
  (filesystem, git, semgrep, sequential-thinking) and
  the security-scanner pattern for vetting third-party servers.
- Sample `.mcp.json.example` (committed) — `.mcp.json` itself goes
  into `.gitignore`. Document why: `.mcp.json` may contain user-
  specific paths or credentials.
- **No auto-install.** User chooses what to wire up.

**GAP-EXT-021 — `lint-agents.sh` quality gate.**

- `{{cookiecutter.project_slug}}/scripts/lint-agents.sh`
  implementing the static-analysis layer:
  - `EMPTY_DESCRIPTION` — every agent and command has a non-empty
    `description` field of ≥3 words.
  - `MISSING_TRIGGER` — slash-command files have `description` and
    `argument-hint` (or are explicitly argument-free) in
    frontmatter.
  - `BLOATED_SKILL` — SKILL.md body ≤6 KiB.
  - `ORPHAN_REFERENCE` — file paths referenced in agent/command
    bodies exist in repo.
  - `DEAD_CROSS_REF` — markdown links resolve.
  - `OVER_CONSTRAINED` — agent prompts have ≤10 "MUST NOT" rules
    (warning, not block).
- `Makefile`: `make lint-agents`. Add to `make validate`.

**GAP-EXT-023 — just (justfile) alternative.**

- Conditional on `task_runner=just` (new cookiecutter variable;
  default `make`).
- `{{cookiecutter.project_slug}}/justfile` with the same targets
  as `Makefile`.
- `hooks/post_gen_project.py` removes whichever isn't selected.

**GAP-EXT-024 — Onboarding automation.**

- `{{cookiecutter.project_slug}}/scripts/bootstrap.sh` — detects
  OS, installs uv, Node 20+, pre-commit, gh CLI via the system
  package manager (brew on macOS, apt on Debian/Ubuntu, dnf on
  Fedora). Idempotent. Then runs `make sync`.
- Update `.claude/commands/start.md` to detect missing tools and
  print install instructions per OS.
- Update README quickstart to reference both
  (`./scripts/bootstrap.sh` for new contributors, `make sync` for
  ones who already have prerequisites).

**Phase 15 gate:**
- `make validate` passes including new `lint-agents` step.
- All new commands/agents/hooks pass `lint-agents`.
- `make monitor` produces tail output (smoke).
- `bootstrap.sh` is shellcheck-clean.

Commit on branch `feat/scaffold-phase-15`. Update register. PR.

### Step 6 — Final validation

After all four phases merge, run the full validation pass:

1. From the template root:
   ```bash
   pipx run cookiecutter . --no-input -o /tmp/test-extensions-py/ \
     --extra-context include_codacy=yes include_codecov=yes \
     include_snyk=yes include_sbom=yes include_docs_site=yes \
     include_release_automation=yes include_scorecard=yes \
     include_slsa=yes include_citation=yes include_funding=yes
   pipx run cookiecutter . --no-input -o /tmp/test-extensions-ts/ \
     --extra-context primary_language=typescript include_docs_site=yes \
     include_release_automation=yes include_scorecard=yes \
     task_runner=just
   pipx run cookiecutter . --no-input -o /tmp/test-extensions-min/ \
     --extra-context include_codacy=no include_codecov=no \
     include_snyk=no include_sbom=no include_docs_site=no \
     include_release_automation=no include_scorecard=no \
     include_slsa=no include_citation=no include_funding=no
   ```
2. For each instantiation, verify:
   - `make validate` (or `just validate`) passes.
   - `make hooks-test` passes.
   - `make check-traceability` passes.
   - `make lint-agents` passes.
   - `make deptry` passes (Python / polyglot only).
   - CLAUDE.md is a symlink resolving to AGENTS.md.
   - AGENTS.md is ≤16 KiB.
   - Devcontainer JSON parses.
   - `.github/workflows/scorecard.yml` parses (use `yamllint` if
     available).
3. Write the success artifact:
   `{{cookiecutter.project_slug}}/report/<UTC-timestamp>-extensions-validate-pass.md`
   summarizing which gaps landed and which phases the run
   covered.
4. Open the final PR titled
   `chore(scaffold): land Phase 15 — extensions validation pass`.

### Step 7 — Hard rules during the build

Same as Phases 0–11:

- **No stub markers** anywhere (CRIT-001).
- **No fabricated metrics, dates, or version pins.** Use
  angle-bracket placeholders for unmeasured values.
- **No work on `main`.** Branch per phase.
- **No `--no-verify`.** CRIT-007.
- **No skipping a phase gate.** Stop and surface failures.
- **Stage explicitly.** Never `git add -A`. IMP-004.
- **Update the gap register after each phase.** Status cells
  must reflect reality.

Specific to extensions:

- **AGENTS.md is hand-authored**, not LLM-generated. Princeton
  study: LLM-generated AGENTS.md files reduced success by 2% and
  increased cost by 23%. Be terse and concrete.
- **Don't auto-install MCP servers, OpenSSF badge, or OSS-Fuzz.**
  Document the opt-in path; the user decides.
- **Don't fork to a competing SDD framework.** Document interop;
  ship our model.

### Step 8 — When blocked

Stop and ask if you encounter:

- A choice between two equally-good adoption patterns (e.g.,
  release-please vs semantic-release) — propose 2–3 options with
  tradeoffs.
- A `cookiecutter` Jinja2 conditional that won't render cleanly
  across all language paths.
- A SHA-pinning question for an action you don't recognize.
- A test that suggests a real hook bypass rather than a test bug.
- Any moment where you would otherwise need to make up a metric
  or date.

When asking, propose 2–3 specific options with tradeoffs. I'll
pick.

### Step 9 — Definition of done

The extensions are complete when all hold:

- [ ] Every row in `SWEBOK_GAP_REGISTER_EXTENSIONS.md` reads `landed`.
- [ ] All three test instantiations (Python-full, TS-just,
      polyglot-minimum) pass `make validate` (or `just validate`).
- [ ] Four phase PRs (12, 13, 14, 15) are merged to `main`.
- [ ] The success artifact exists in the most recent test
      instantiation's `report/` directory.
- [ ] No commit in extension history used `--no-verify` or pushed
      to `main` directly.
- [ ] AGENTS.md is the canonical instruction file; CLAUDE.md is
      a symlink.
- [ ] Scorecard workflow runs cleanly on at least one test
      instantiation (or smoke-test simulation).
- [ ] `RESEARCH_FINDINGS.md` Status column reflects current state.

When all eight conditions hold, post a summary in chat with:
- Total file count added (this extension)
- Total commit count (this extension)
- Per-phase landed-gap count
- Cumulative count: Phases 0–11 + 12–15 grand total
- Any deferred-with-justification items (and which ADR records
  the deferral)

---

## END PROMPT

---

## Notes for the human (you)

A few things to keep in mind once the agent is running:

1. **Phase 12 is the riskiest of the four** because it changes
   foundational files (AGENTS.md becomes primary, CLAUDE.md
   becomes a symlink). If any agent runtime in your workflow
   breaks during Phase 12, this is the first place to look.

2. **Phase 13 (OpenSSF) is the highest external-credibility
   payoff.** Your Databricks ISV / partnership conversations
   benefit from "Scorecard ≥7/10" and "SLSA L3 provenance" being
   demonstrable.

3. **The cookiecutter variable surface is now larger.**
   Document the new variables prominently in the top-level README.
   First-time users should not be confronted with 15 questions —
   keep `--no-input` defaults sensible.

4. **The lint-agents.sh check is load-bearing for ongoing health.**
   Every time you add a slash command or agent in any project
   instantiated from this template, this check is what catches the
   common failure modes (empty description, broken cross-ref,
   bloated skill).

5. **AGENTS.md compatibility with Claude Code.** As of the time
   of this writing, Claude Code does not natively support
   AGENTS.md — it reads CLAUDE.md. The symlink workaround is
   stable but if Anthropic ships native AGENTS.md support
   (Issue #6235 has thousands of upvotes), you'll want to revisit
   `hooks/post_gen_project.py` to remove the symlink at that
   point.

6. **MCP server choices are intentionally minimal in our docs.**
   The MCP ecosystem is changing fast. Keeping our recommended
   list short (filesystem, git, semgrep, sequential-thinking)
   means our docs stay accurate longer.

7. **Reuse the `/sync` discipline on this template repo itself.**
   After each phase merge, run `/sync` on the template. The
   template eats its own cooking — that's the dogfood test for
   the whole methodology.

That's the full extension handoff. Open VS Code Insiders, paste the
prompt, and the build runs from there.
