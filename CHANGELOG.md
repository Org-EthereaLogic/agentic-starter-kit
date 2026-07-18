<!--
  Keep-a-Changelog re-uses subsection headings (`Added`, `Changed`,
  `Fixed`) under every version, which trips MD024 in markdownlint's
  default config. Scope the suppression to this file.
-->
<!-- markdownlint-disable-file MD024 -->

# Changelog

All notable changes to **agentic-starter-kit** (the template repository
itself) are documented in this file.

The format is loosely based on [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
Pre-1.0 releases bump the **minor** version on breaking changes and the
**patch** version on bug fixes.

> **Scope.** This file tracks template-source changes only — i.e.
> things adopters care about when they re-render or run
> `copier update`. Generated projects keep their own `CHANGELOG.md`,
> maintained by `release-please` against their own commit history.
>
> **Authoritative source.** Each entry below summarizes the
> corresponding [GitHub Release](https://github.com/Org-EthereaLogic/agentic-starter-kit/releases)
> and the merged PRs. Read the linked release for the full story; this
> file is the offline index.
>
> **Path conventions.** Filesystem paths below describe the **rendered
> project** layout (`.claude/commands/`, `.devcontainer/`,
> `docs/THREAT_MODEL.md`, …) — what an adopter sees after running
> `cookiecutter` or `copier`. In this template repository's own
> source tree those same paths live under
> `{{cookiecutter.project_slug}}/`. The rendered-project view is
> what's actionable for adopters reading release impact, so the
> changelog uses it.

---

## [Unreleased]

### Security

- **Git-layer protected-branch enforcement is now the primary CRIT-008
  boundary.** New checked-in git hooks `.githooks/pre-commit`,
  `.githooks/pre-merge-commit`, and `.githooks/pre-push` (POSIX `sh`,
  language-neutral) block, on a protected branch (the render-time default
  branch plus `master`): direct commits and `--amend` (`pre-commit`),
  merge commits from a non-fast-forward conflict-free `git merge`
  (`pre-merge-commit`), and all pushes (`pre-push`). Because they run
  **after** the shell resolves the command, they cannot be dodged by the
  shell idioms that defeat a command-string matcher — `eval`, `exec`,
  `\git`, `git${IFS}push`, `bash -cl`, `sudo`/`doas`, `stdbuf`/`setsid`,
  and `&` chains — the bypass classes issue
  [#102](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/102)
  showed a string-layer hook cannot fully close. `pre-push` also blocks
  refspec pushes (`feat/x:main`), `--all`/`--mirror`, implicit-upstream
  pushes, and deletes of a protected ref.
- **Honest coverage scope is documented, not overclaimed.** Git invokes
  **no** commit-time hook for a conflict-free
  `cherry-pick`/`revert`/`rebase`/`am` replaying commits directly onto a
  **local** protected branch, so the git layer does not stop those
  landing locally. The backstops — documented in `.githooks/README.md`,
  `DIRECTIVES.md`, and `docs/THREAT_MODEL.md`, and exercised by
  `tests/test_git_hooks.sh` — are `pre-push` (blocks pushing the result
  to the protected remote), the agent-layer hook (blocks the porcelain/
  `eval`/`\git` forms an agent would issue), and server-side branch
  protection (the true backstop).
- **`.claude/hooks/pre-tool-use.js` is re-labeled defense-in-depth.**
  The Claude Code `PreToolUse:Bash` hook (including the issue #102
  regex hardening) is retained as a fast, agent-facing early block, but
  is now documented as best-effort — **not** the CRIT-008 guarantee.
  Its header, `.claude/hooks/README.md`, `DIRECTIVES.md` CRIT-008,
  `governance-rules.yaml`, and `docs/THREAT_MODEL.md` all name the
  git-layer hook as the enforced boundary and document the honest scope
  (an operator-integrity control, not a sandbox: a user can unset
  `core.hooksPath`; server-side branch protection is the real backstop).

### Added

- **`make hooks-install`** wires the boundary idempotently
  (`git config core.hooksPath .githooks`) and is a prerequisite of
  `make hooks-test` (hence `make validate`). It is also wired into
  `.devcontainer/post-create.sh` and surfaced in the cookiecutter
  post-generation "Next steps". `core.hooksPath` supersedes
  `pre-commit install`; the hooks **chain** to `pre-commit hook-impl`
  when the framework is present so its hooks keep running.
- **`.claude/hooks/pre-tool-use.js` gains two agent-layer wrapper
  classes** (defense-in-depth for `pre-merge-commit`): `eval
  '<payload>'`/`eval "<payload>"` is peeled and its payload recursively
  evaluated, and a leading backslash on the command token (`\git`) is
  stripped before the git check — so `eval 'git cherry-pick …'` and
  `\git merge …` on a protected branch are caught early, while read-only
  and non-git payloads still pass.
- **`tests/test_git_hooks.sh`** — a language-neutral POSIX `sh`
  regression suite (never pruned, run unconditionally by
  `make hooks-test`) that installs the hooks in a throwaway temp repo
  with a local bare remote and asserts every bypass idiom is blocked on
  a protected target while feature-branch commits/pushes still succeed.
  It also asserts `git merge --no-ff` (and its `eval`/`\git` spellings)
  into a protected branch is blocked by `pre-merge-commit`, that a
  feature-branch merge still succeeds, and — for the documented git
  limitation — that a `cherry-pick`/`revert` onto a protected branch
  lands locally but the subsequent push is blocked by `pre-push`. Idioms
  whose wrapper is absent or non-interactive (`setsid`, `sudo`, `doas`)
  are skipped with a recorded reason, never assumed-pass.
- **`.githooks/README.md`** documenting the hooks, the install, the
  pre-commit-framework chaining, and the honest boundary.
- `scripts/check-governance.sh` now asserts the `.githooks` hooks
  (`pre-commit`, `pre-merge-commit`, `pre-push`) exist and are executable
  and that the `core.hooksPath` install wiring is checked in (repo-state
  facts only, so a fresh render / CI checkout stays green).

### Fixed

- **`--gate audit` lookup is no longer dead.**
  `GovernanceRules.get_for_enforcement_gate()` only read the
  comma-separated `rule` string key, but the `audit` entry in
  `governance-rules.yaml` uses a `rules:` YAML list, so the gate
  always resolved to zero directives and
  `scripts/lib/governance.py --gate audit` exited 1 with
  `ERROR: Unknown gate: audit` even though the gate exists. The
  loader now accepts both key shapes (and tolerates a mis-authored
  scalar `rules` value instead of char-splitting it); `rule`-string
  gates (`marker_scan`, `governance_check`, `hooks_test`,
  `action_pins`) are unaffected. The `--gate` CLI now distinguishes an
  unknown gate name from a gate that is defined but resolves to no
  known directives, via a new `has_enforcement_gate()` check, rather
  than reporting both as `Unknown gate`.
  ([#103](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/103))
- **`scripts/check-governance.sh` no longer vacuously passes CRIT-002
  when the governance loader crashes.** The script filled its
  `required_files`, `required_agents`, `required_skills`, and
  `optional_dirs` arrays from `while read` loops over process
  substitutions piping `scripts/lib/governance.py --list-...`. Under
  `set -euo pipefail`, a process substitution's exit status is
  invisible to the enclosing loop, so a loader crash (corrupt
  `governance-rules.yaml`, missing PyYAML) silently left every
  loader-driven array empty, every affected check was skipped, and
  the script still reached `report_status` and printed
  `governance-check OK`. All four loads now capture the loader's raw
  output into a plain variable first, guard it with `if ! var="$(...)"`
  so the loader's exit code propagates, fail loudly with a diagnostic
  naming the exact loader invocation, and exit non-zero before any
  downstream check or the success line can run. (`scripts/marker-scan.sh`
  retains an unguarded `done < <(...)` read for `--list-marker-surfaces`
  with a milder instance of the same risk; it is tracked separately.)
  ([#104](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/104))
- **`Makefile.fragments/typescript.mk`'s `test-typescript` recipe no
  longer reports success on a failing JS test.** The recipe chained
  `find ... | head -1 >/dev/null && find ... | xargs -r node --test ||
  echo "WARN: no JS test files found"`; the trailing `|| echo` bound
  to the whole `&&` chain, so a real `node --test` failure was
  swallowed and the recipe exited 0 (and mis-printed the "no test
  files found" message on a genuine failure). Because `make test` and
  `make validate` aggregate `test-typescript`, a red JavaScript suite
  passed CI. The recipe now uses an explicit grouped-`find` existence
  check (inside the `if` condition, so a "no matches" status can't
  trip errexit) to choose between WARN-and-exit-0 (genuinely no test
  files) and running `find tests -type f \( ... \) -exec node --test
  {} +`, whose exit status now propagates on a real failure. The
  GNU-only `xargs -r` was dropped for POSIX portability, and
  `*.test.cjs` discovery was added — deliberately without a matching
  `test_*.cjs` pattern — so `tests/test_audit_hooks.cjs` (still owned
  by `hooks.mk`) is never picked up.
  ([#105](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/105))

---

## [0.7.2] - 2026-05-08

Patch release fixing a CI-workflow regression that has been silently
breaking every Python / polyglot scaffold since v0.4.0, plus a much
friendlier error path when the dev container's outbound network is
blocked.

### Fixed

- **`Supply-chain audit` workflow now actually runs.**
  `pypa/gh-action-pip-audit` passes its `inputs:` parameter to
  pip-audit's `--requirement` flag, which only understands
  `requirements.txt` format. The workflow was passing
  `pyproject.toml` directly, failing on the first `[project]` TOML
  header. Fix: export uv's resolved lock with
  `uv export --no-emit-project --no-hashes --all-extras
  --format requirements-txt --output-file requirements.audit.txt`
  and audit the resulting file.
  ([#100](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/100))
- **`post-create.sh` now diagnoses outbound-network blocks up
  front.** When VS Code's "Restricted Network Access", Codespaces'
  restricted-internet policy, GitHub Copilot Coding Agent's
  outbound firewall, or a corporate proxy blocks the container,
  every downstream `apt-get`, `uv`, `npm`, and `gh` call fails with
  a tool-specific cryptic error. The new `check_outbound_network`
  step probes `pypi.org` with a 5-second timeout and, on failure,
  prints the four common 2026 causes plus a pointer to
  `KNOWN-ISSUES.md`. Non-fatal — legitimate offline flows keep
  working.
  ([#100](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/100))

### Added

- **`KNOWN-ISSUES.md` "Dev container internet access blocked"
  entry** with declarative remediation snippets for each of the
  four causes (VS Code dialog trust, Codespaces UI, Copilot Coding
  Agent firewall, corporate proxy via `containerEnv`).
  ([#100](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/100))

[Full release notes](https://github.com/Org-EthereaLogic/agentic-starter-kit/releases/tag/v0.7.2)
· [Diff: v0.7.1...v0.7.2](https://github.com/Org-EthereaLogic/agentic-starter-kit/compare/v0.7.1...v0.7.2)

---

## [0.7.1] - 2026-05-08

Patch release addressing two adopter-blocking dev-container bugs
surfaced when the first real project (`ai-powered-lead-gen-mvp`)
scaffolded from v0.7.0, plus two doc-drift fixes that landed on
the way.

### Fixed

- **Editor attach no longer races `make sync`.**
  `devcontainer.json` declared `postCreateCommand` but no
  `waitFor` directive. VS Code attached and the Python + Ruff
  extensions tried to spawn `${workspaceFolder}/.venv/bin/python`
  before the post-create script created it. Adding
  `"waitFor": "postCreateCommand"` blocks editor attach until
  post-create exits.
  ([#99](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/99))
- **`make sync` self-heals a non-runnable `.venv`.**
  `uv sync` writes lockfile and metadata but does not detect that
  `.venv/bin/python` itself is a dangling symlink (e.g. after a
  base-image upgrade or device migration). `sync-python` now
  removes the venv before re-syncing when
  `.venv/bin/python --version` fails. Idempotent on fresh trees.
  ([#99](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/99))
- **`docs/THREAT_MODEL.md` `Status` column reflects shipped
  controls.** SLSA L3 provenance, `pip-audit` / `npm audit`,
  SHA-pinned-action verification, the MCP policy doc, and the
  `report/audit.jsonl` audit trail were all marked
  `pending Phase A3 / A4 / A5` even though they had landed in
  v0.4.0; the table now reads honestly. Mirrored in
  `docs/SWEBOK_GAP_REGISTER_EXTENSIONS.md` for `GAP-EXT-004`
  (SLSA) and `GAP-EXT-020` (MCP).
  ([#97](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/97))

### Added

- **`KNOWN-ISSUES.md` "Dev container" section** documenting the
  Ruff `ENOENT` race symptom and the stale-`.venv` symptom with
  recovery steps for adopters whose containers were created
  against v0.7.0.
  ([#99](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/99))
- **Root `CHANGELOG.md`** seeded from GitHub Releases v0.4.0 –
  v0.7.0 in Keep-a-Changelog 1.1.0 format. Adopters can now read
  template release history offline, on forks, or in clones
  without a round-trip to github.com.
  ([#98](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/98))

[Full release notes](https://github.com/Org-EthereaLogic/agentic-starter-kit/releases/tag/v0.7.1)
· [Diff: v0.7.0...v0.7.1](https://github.com/Org-EthereaLogic/agentic-starter-kit/compare/v0.7.0...v0.7.1)

---

## [0.7.0] - 2026-05-08

Slash-command rename plus dev-container compat hardening, surfaced by
a three-variant build exercise (Python defaults, TypeScript minimal,
polyglot kitchen-sink) running on host **and** inside the official
`.devcontainer/`.

### Changed

- **BREAKING (template surface):** the 16 `.claude/commands/*.md`
  files now ship as plain verbs (`audit.md`, `plan.md`, `sync.md`, …)
  invoked as `/<verb>`. The historical "never re-prefix" contract is
  reversed; the original Spec Kit collision concern is moot now that
  `/speckit.*` shipped. ([#92](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/92))

### Fixed

- Resolve cwd via `realpathSync` in the TS audit-hooks test so
  `make hooks-test` no longer fails on macOS hosts where `/var` is a
  symlink to `/private/var`. Linux unaffected.
  ([#93](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/93))
- Make SBOM references in `THREAT_MODEL.md` truly conditional on
  `include_sbom`; broken `scripts/generate-sbom.sh` references are no
  longer rendered into `sbom=no` projects.
  ([#94](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/94),
  [#96](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/96))
- Three dev-container compatibility fixes from the build exercise:
  governance scripts resolve a venv-aware Python so PyYAML is
  available in clean dev containers; `evals.mk` guards `$CI` with
  `${CI:-}` so it does not trip `set -u` on GNU Make 4+;
  `test_npm_install_failure_is_non_fatal` pins a minimal `PATH` so
  pre-installed AI CLIs in the dev container do not short-circuit the
  npm-failure branch.
  ([#95](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/95))

[Full release notes](https://github.com/Org-EthereaLogic/agentic-starter-kit/releases/tag/v0.7.0)
· [Diff: v0.6.0...v0.7.0](https://github.com/Org-EthereaLogic/agentic-starter-kit/compare/v0.6.0...v0.7.0)

---

## [0.6.0] - 2026-05-08

Three PRs since v0.5.0: one new feature and two targeted fixes.

### Added

- **AI CLIs installed in devcontainer post-create.** `ensure_ai_clis()`
  added to `.devcontainer/post-create.sh` so rendered projects land
  with `claude` (`@anthropic-ai/claude-code`), `codex`
  (`@openai/codex`), `gemini` (`@google/gemini-cli`), and `gh copilot`
  available out of the box. Installs are best-effort
  (logs-and-continues on failure) and idempotent (no-op when the
  binary is already on `PATH`). A writable-prefix guard handles plain
  container images without nvm. Six new regression tests cover the
  key behaviours.
  ([#90](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/90))

### Fixed

- Pinned all unpinned Actions in the template-smoke-test workflow,
  completing the SHA-pinning work from #87.
  ([#89](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/89))
- Resolved 8 of 11 `check-doc-drift` false positives and stale
  references. Every rendered project previously emitted 11 warnings
  on `make validate`; now emits 3 (intentional Phase-8 traceability
  placeholders).
  ([#91](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/91))

[Full release notes](https://github.com/Org-EthereaLogic/agentic-starter-kit/releases/tag/v0.6.0)
· [Diff: v0.5.0...v0.6.0](https://github.com/Org-EthereaLogic/agentic-starter-kit/compare/v0.5.0...v0.6.0)

---

## [0.5.0] - 2026-05-08

Four template features, one security-relevant CI hardening, drops one
no-op variable, and bumps polish across docs and tests.

### Added

- **Sentinel-based `pyproject.toml` pruning.** The template ships a
  single valid-TOML `pyproject.toml`; the post-gen hook strips
  variant-tagged content (typechecker, SBOM dev-deps) so editors and
  TOML language servers can parse the source on disk.
  ([#81](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/81))
- **Language-mismatched QUICKSTART pruning.** The QUICKSTART for the
  unselected language path no longer ships in the rendered tree.
  ([#80](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/80))
- **`governance-rules.yaml` drives the governance gates.** The
  five-layer governance stack is now data-driven from a single YAML
  file rather than scattered checks.
  ([#79](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/79))
- **Data-driven hook regression tests.** The pre-tool-use hook test
  suite reads scenarios from a JSON spec, keeping the Python and Node
  test runners in lockstep.
  ([#76](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/76))

### Changed

- Every third-party GitHub Action in the rendered project's workflows
  is now SHA-pinned (IMP-006). `check-action-pins` is strict by
  default; the SLSA generator stays tag-pinned per upstream policy
  and is allow-listed.
  ([#87](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/87))
- Rendered README dev-tool list is now language-conditional;
  previously hardcoded `ruff, ty, pytest` for TypeScript-only
  renders.
  ([#84](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/84))
- `make validate` honestly runs lint, typecheck, and test.

### Removed

- **BREAKING (cookiecutter variable surface, functionally
  no-op):** `include_databricks` removed. It was a documented no-op
  placeholder and will return when actual Databricks scaffolding is
  designed. Copier silently ignores the dropped variable in existing
  answers files, so `copier update` from v0.4.x is safe.
  ([#88](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/88))

[Full release notes](https://github.com/Org-EthereaLogic/agentic-starter-kit/releases/tag/v0.5.0)
· [Diff: v0.4.0...v0.5.0](https://github.com/Org-EthereaLogic/agentic-starter-kit/compare/v0.4.0...v0.5.0)

---

## [0.4.0] - 2026-05-06

First stable release. All 15 roadmap issues across Phases A
(Hardening), B (Specialization), C (Distribution), and D (Polish) are
closed.

### Added

#### Phase A — Hardening

- **A1:** OWASP Agentic Top 10 (2026) coverage matrix in
  `docs/THREAT_MODEL.md`.
  ([#10](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/10))
- **A2:** Astral toolchain default — `uv` + `ruff` + `ty`.
  ([#11](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/11))
- **A3:** Supply-chain hardening — SLSA L3 provenance via
  `slsa-framework/slsa-github-generator`, OSSF Scorecards,
  `pip-audit`, `npm audit`, optional Macaron analysis.
  ([#12](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/12))
- **A4:** MCP server baseline — read-only filesystem, read-only git,
  GitHub gated by fine-grained PAT — plus `docs/MCP_POLICY.md`.
  ([#13](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/13))
- **A5:** Hook surface extension and the `report/audit.jsonl`
  append-only audit trail (SessionStart, UserPromptSubmit,
  PostToolUse hooks).
  ([#14](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/14))

#### Phase B — Specialization

- **B1:** Eight specialized Claude Code agents under
  `.claude/agents/`.
  ([#15](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/15))
- **B2:** Sixteen `/gov.*` slash commands with frontmatter and tool
  allowlists. *(Renamed in v0.7.0 — see [#92](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/92).)*
  ([#16](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/16))
- **B3:** `.claude/skills/` progressive-disclosure starter skills.
  ([#17](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/17))
- **B4:** `prompts/` + `evals/` + promptfoo + `make eval` gate.
  ([#18](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/18))

#### Phase C — Distribution

- **C1:** `copier.yml` dual-mode template parallel to
  `cookiecutter.json`.
  ([#19](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/19))
- **C2:** `governance-review` CLI validator.
  ([#20](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/20))
- **C3:** Devcontainer + SHA-pinned Dockerfile.
  ([#21](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/21))
- **C4:** MkDocs Material docs site (optional).
  ([#22](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/22))
- **C5:** Commitizen + release-please for generated projects.
  ([#23](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/23))

#### Phase D — Polish

- **D1:** Examples gallery — Day 1 / Day 7 vignettes.
  ([#24](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/24))

#### Post-roadmap stabilization

- Cluster A (#45) — convention drift fixes, `KNOWN-ISSUES.md`,
  first-commit walkthrough, Node soft-check in `hooks-test`.
- Action-pin validator (forbids bare `@v1` refs in workflows).
- Cookiecutter `__prompts__` for per-variable descriptions.
- Codacy runtime + tool configuration.

### Verified

- `make validate` on the rendered scaffold runs end-to-end:
  governance-review → marker-scan → governance-check →
  traceability → doc-drift → action-pins → hooks-test → lint →
  typecheck → test → eval (when `include_promptfoo=yes`).
- OSSF Scorecards target ≥ 7/10 on rendered smoke projects.

[Full release notes](https://github.com/Org-EthereaLogic/agentic-starter-kit/releases/tag/v0.4.0)

---

## Earlier history

Pre-v0.4.0 history was iterative scaffolding without published
releases; the build plan, methodology, and gap registers under
`docs/` are the authoritative record for that period.

---

[Unreleased]: https://github.com/Org-EthereaLogic/agentic-starter-kit/compare/v0.7.2...HEAD
[0.7.2]: https://github.com/Org-EthereaLogic/agentic-starter-kit/releases/tag/v0.7.2
[0.7.1]: https://github.com/Org-EthereaLogic/agentic-starter-kit/releases/tag/v0.7.1
[0.7.0]: https://github.com/Org-EthereaLogic/agentic-starter-kit/releases/tag/v0.7.0
[0.6.0]: https://github.com/Org-EthereaLogic/agentic-starter-kit/releases/tag/v0.6.0
[0.5.0]: https://github.com/Org-EthereaLogic/agentic-starter-kit/releases/tag/v0.5.0
[0.4.0]: https://github.com/Org-EthereaLogic/agentic-starter-kit/releases/tag/v0.4.0
