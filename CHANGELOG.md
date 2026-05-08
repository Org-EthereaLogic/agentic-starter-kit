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

---

## [Unreleased]

No unreleased changes.

---

## [0.7.0] — 2026-05-08

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

## [0.6.0] — 2026-05-08

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

## [0.5.0] — 2026-05-08

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

## [0.4.0] — 2026-05-06

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

[Unreleased]: https://github.com/Org-EthereaLogic/agentic-starter-kit/compare/v0.7.0...HEAD
[0.7.0]: https://github.com/Org-EthereaLogic/agentic-starter-kit/releases/tag/v0.7.0
[0.6.0]: https://github.com/Org-EthereaLogic/agentic-starter-kit/releases/tag/v0.6.0
[0.5.0]: https://github.com/Org-EthereaLogic/agentic-starter-kit/releases/tag/v0.5.0
[0.4.0]: https://github.com/Org-EthereaLogic/agentic-starter-kit/releases/tag/v0.4.0
