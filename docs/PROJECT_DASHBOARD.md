# Project Dashboard — agentic-starter-kit Roadmap

> Local mirror of the canonical GitHub Project board. The source of
> truth is GitHub; this file is regenerated periodically (see
> *Refresh* at the bottom). Status reflects the most recent local
> sync.

| Surface | Link |
| --- | --- |
| GitHub Project (board) | <https://github.com/orgs/Org-EthereaLogic/projects/6> |
| Issues (filtered to roadmap) | <https://github.com/Org-EthereaLogic/agentic-starter-kit/issues?q=is%3Aissue+label%3Aphase-a%2Cphase-b%2Cphase-c%2Cphase-d> |
| Milestones | <https://github.com/Org-EthereaLogic/agentic-starter-kit/milestones> |

---

## Plan summary

The roadmap is divided into four phases. Each phase ended in a
publishable release. **Phase A → v0.2; Phase B → v0.3; Phase C →
v0.4 (+ v0.4.1 hotfix). Phase D — Polish — was originally deferred,
then shipped opportunistically alongside Phase C.**

| Phase | Name | Release | Issues | Total effort (days) | Status |
| --- | --- | --- | --- | --- | --- |
| A | Hardening | v0.2, 2026-05-03 | 5 | 9 | ✅ shipped |
| B | Specialization | v0.3, 2026-05-06 | 4 | 9 | ✅ shipped |
| C | Distribution | v0.4 + v0.4.1, 2026-05-06 | 5 | 10 | ✅ shipped |
| D | Polish | 2026-05-06 | 1 | 2 | ✅ shipped |
| — | Post-roadmap fixes | v0.4 / v0.4.1 hotfixes | 9 | ~10 | ✅ shipped |

Status legend: 📋 Todo · 🟡 In Progress · ✅ Done · ⏸ Deferred

**Current state (2026-07-20):** all roadmap work and the original
optimization set (#69–#74) are merged. The v0.7.x release-hardening
batch (#87–#101) and the July governance-hardening batch have also
shipped: #102/#112, #103/#113 with the #115 precedence-pin follow-up,
plus #104/#118, #108/#123, #105/#121, #106/#126, #107/#128,
#109/#130, #110/#132, #133/#136, #135/#138, #119/#140, and #111/#148.
The local CI (`scripts/local-ci/`) is now the adopted interim gate (#145). The
current follow-on queue is
[#144 and #147](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues?q=is%3Aopen+is%3Aissue):
an order-sensitive test selecting the intentionally skipped agent `README.md`
instead of an agent definition on Linux (#144), root-owned npm-cache descendants
blocking TypeScript and polyglot deep-matrix legs (#147), and two PR #148
direct `pytest.skip` calls that `ty` rejects in both keyword and positional
forms after those defects are fixed. Their template-source-only conditions now
use the file's existing accepted `@pytest.mark.skipif(..., reason=...)` pattern.
#111's refactoring/optimization epic shipped via #148 (#1/#2 were already
covered by #110/#132). Sprint 1
(2026-05-06 → 2026-05-19) was never populated and its window has closed.

## Field verification — #144 / #147 candidate (2026-07-20)

These are measured local-CI results for the PR #150 candidate, not hosted
GitHub Actions results. The shipped code commit is
`dd82f8921df98b3e2c4aa146ddf77281047cfee7`; retained focused evidence used
the pre-ship test commit `916b0468e0608ea096bd22dab9d5d514421813a3`.

- **#144 focused regression:**
  `uv run --with pytest python -m pytest
  '{{cookiecutter.project_slug}}/tests/test_skill_contracts.py::SkillContractTests::test_governance_check_rejects_body_only_agent_key'
  -q` passed on macOS (`1 passed in 0.38s`) and in the Linux/arm64 local-CI
  image (`1 passed in 0.10s`). The test selected the sorted non-README agent
  and asserted that `check-governance.sh` returned nonzero with `missing
  required frontmatter` after the body-only model-key mutation. The complete
  `test_skill_contracts.py` run passed (`10 passed in 2.39s`).
- **Tier 1 at the shipped commit:** the tracked pre-push gate passed with
  `pytest` in 7s and default render smoke in 1s:
  `{"event":"gate","run_id":"20260720T044837Z","git_commit":"dd82f8921df98b3e2c4aa146ddf77281047cfee7","branch":"adws/job_20260720_0003/issues-144-147-deep-green","dirty":false,"overall":"pass","steps":[{"step":"pytest","status":"pass","duration_s":7},{"step":"render-smoke","status":"pass","duration_s":1}]}`.
- **#147 arbitrary UID/GID:** the Linux/arm64 image run with `--user
  12345:23456` reported `uid=12345 gid=23456 cache-write=PASS
  npm-cache-verify=PASS` (exit 0). The audit found no existing
  `/opt/npm-cache` file or directory lacking other-write permission, and a
  non-root descendant create/write passed; runtime `--user` behavior and
  permissions outside `/opt/npm-cache` were unchanged.
- **Focused deep legs and preserved skips:**
  `RUN_VALIDATE=1 TOOLS_OVERRIDE=cookiecutter
  VARIANTS_OVERRIDE=python-mit-ty make ci-orb` passed at `916b046` (repo
  pytest plus cookiecutter `python-mit-ty` in 7s; overall 14s).
  `RUN_VALIDATE=1 VARIANTS_OVERRIDE=typescript-mit make ci-orb` passed at
  `916b046` (cookiecutter 5s, copier 4s, render equivalence pass; overall
  16s). Direct `pytest.skip` calls are absent; focused template-source
  execution retained the two unchanged skip reasons and reported exactly
  `2 skipped in 0.02s`. The Python ty deep leg and all six ty-selected legs
  in the complete matrix passed.
- **Fresh complete matrix at the shipped commit:** from a clean,
  self-contained clone pinned to `dd82f89`, `RUN_VALIDATE=1 make ci-orb`
  exited 0 and passed repo-root pytest, all seven variants under both
  cookiecutter and copier (14 renderer/variant legs), and render equivalence
  in 117s. Complete matrix record:

```json
{"event":"orb_matrix","run_id":"20260720T045653Z","git_commit":"dd82f8921df98b3e2c4aa146ddf77281047cfee7","run_validate":"1","overall":"pass","legs":[{"step":"pytest","status":"pass"},{"tool":"cookiecutter","variant":"python-mit-ty","language":"python","status":"pass","duration_s":11},{"tool":"copier","variant":"python-mit-ty","language":"python","status":"pass","duration_s":7},{"tool":"cookiecutter","variant":"python-mit-mypy","language":"python","status":"pass","duration_s":8},{"tool":"copier","variant":"python-mit-mypy","language":"python","status":"pass","duration_s":9},{"tool":"cookiecutter","variant":"python-apache-sbom-ty","language":"python","status":"pass","duration_s":7},{"tool":"copier","variant":"python-apache-sbom-ty","language":"python","status":"pass","duration_s":7},{"tool":"cookiecutter","variant":"typescript-mit","language":"typescript","status":"pass","duration_s":6},{"tool":"copier","variant":"typescript-mit","language":"typescript","status":"pass","duration_s":4},{"tool":"cookiecutter","variant":"typescript-apache-tools","language":"typescript","status":"pass","duration_s":4},{"tool":"copier","variant":"typescript-apache-tools","language":"typescript","status":"pass","duration_s":4},{"tool":"cookiecutter","variant":"polyglot-mit-all-ty","language":"polyglot","status":"pass","duration_s":10},{"tool":"copier","variant":"polyglot-mit-all-ty","language":"polyglot","status":"pass","duration_s":10},{"tool":"cookiecutter","variant":"polyglot-mit-all-macaron-mypy","language":"polyglot","status":"pass","duration_s":11},{"tool":"copier","variant":"polyglot-mit-all-macaron-mypy","language":"polyglot","status":"pass","duration_s":12},{"step":"render-equivalence","status":"pass"}]}
```

Runner note: the first required invocation directly from the linked worktree
produced `{"event":"orb_ci","run_id":"20260720T045610Z","git_commit":"dd82f8921df98b3e2c4aa146ddf77281047cfee7","duration_s":0,"overall":"fail"}`
before any matrix leg ran: the container could not resolve the bind-mounted
worktree's host-only `.git/worktrees/...` target and reported `clone failed`.
The self-contained exact-commit clone above removed only that runner-layout
constraint; no source file changed between the failed invocation and the
passing matrix.

---

## Phase A — Hardening (v0.2, shipped 2026-05-03)

| ID | Issue | Title | Gap | Lev | Eff | Status |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | [#10](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/10) | OWASP Agentic Top 10 (2026) coverage matrix | G1 | High | 2 | ✅ |
| A2 | [#11](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/11) | Astral toolchain default (uv + ruff + ty) | G3 | Medium | 1 | ✅ |
| A3 | [#12](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/12) | Supply-chain hardening (SLSA + OSSF + audit + Macaron) | G4 | High | 3 | ✅ |
| A4 | [#13](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/13) | MCP server baseline + policy | G5 | Medium | 1 | ✅ |
| A5 | [#14](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/14) | Hook surface extension + audit trail | G7 | High | 2 | ✅ |

**Phase A gate:** `make validate` passes; OSSF Scorecards ≥ 7/10 on the rendered smoke project.

## Phase B — Specialization (v0.3, shipped 2026-05-06)

| ID | Issue | Title | Gap | Lev | Eff | Status |
| --- | --- | --- | --- | --- | --- | --- |
| B1 | [#15](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/15) | Author 8 specialized Claude Code agents | G10 | High | 3 | ✅ |
| B2 | [#16](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/16) | Author 16 unprefixed slash commands | G2, G10 | High | 3 | ✅ |
| B3 | [#17](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/17) | Add `.claude/skills/` with starter skills | G6 | Medium | 1 | ✅ |
| B4 | [#18](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/18) | `prompts/` + `evals/` + promptfoo + `make eval` | G2 | Medium | 2 | ✅ |

**Phase B gate:** every command/agent has YAML frontmatter; agents-coverage check in `make validate`; command ↔ `/speckit.*` mapping table complete.

## Phase C — Distribution (v0.4 + v0.4.1, shipped 2026-05-06)

| ID | Issue | Title | Gap | Lev | Eff | Status |
| --- | --- | --- | --- | --- | --- | --- |
| C1 | [#19](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/19) | Add `copier.yml` dual-mode template | G9 | High | 4 | ✅ |
| C2 | [#20](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/20) | `governance-review` CLI validator | G11 | Medium | 3 | ✅ |
| C3 | [#21](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/21) | Devcontainer + Dockerfile | G8 | Medium | 1 | ✅ |
| C4 | [#22](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/22) | MkDocs Material docs site (optional) | — | Low | 1 | ✅ |
| C5 | [#23](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/23) | Commitizen + release-please | G12 | Low | 1 | ✅ |

**Phase C gate:** a 6-month-old smoke project absorbs every Phase A/B/C addition via `copier update` without merge conflicts on locked governance files.

## Phase D — Polish (shipped 2026-05-06)

| ID | Issue | Title | Gap | Lev | Eff | Status |
| --- | --- | --- | --- | --- | --- | --- |
| D1 | [#24](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/24) | Examples gallery / vignettes | — | Low | 2 | ✅ |

## Completed optimization roadmap (filed 2026-05-06)

Sourced from `docs/OPTIMIZATION_ROADMAP.md`. The other six items
in that doc (#1–#4, #6, #7) shipped during Phases A–C; the six
follow-on issues below closed on 2026-05-07.

| ID | Issue | Title | Lev | Eff | Status |
| --- | --- | --- | --- | --- | --- |
| O5 | [#69](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/69) | Consolidate Python/TypeScript hook test maintenance | High | 1 | ✅ |
| O8 | [#70](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/70) | Integration test for post-gen hook file pruning | Medium | 1 | ✅ |
| O9 | [#71](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/71) | Jinja2 filter library for template-side helpers | Low | 1 | ✅ |
| O10 | [#72](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/72) | Extract governance rules to data-driven config | Medium | 1 | ✅ |
| O11 | [#73](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/73) | Language-specific quickstart guides | Medium | 1 | ✅ |
| O12 | [#74](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/74) | Language/tool comparison matrix in README | Low | 1 | ✅ |

## Post-roadmap fixes (May 5–6, 2026)

Discovered during the first real-world build of `campaign-pulse` from
the kit. All shipped via v0.4 + v0.4.1.

| Issue | Title | Area | Status |
| --- | --- | --- | --- |
| [#38](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/38) | Pin `pypa/gh-action-pip-audit` to a published tag | ci | ✅ |
| [#39](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/39) | Pin `ossf/scorecard-action` to a published tag | ci | ✅ |
| [#40](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/40) | Dependabot `docker /.devcontainer` errors on empty dir | ci | ✅ |
| [#41](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/41) | gitleaks-action requires paid `GITLEAKS_LICENSE` | ci | ✅ |
| [#42](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/42) | macOS `/var → /private/var` symlink test failure | hooks | ✅ |
| [#43](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/43) | `check-doc-drift.sh` requires Bash 4+ (macOS ships 3.2) | tooling | ✅ |
| [#44](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/44) | CycloneDX SBOM job fails with exit code 2 | ci | ✅ |
| [#45](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/45) | Convention drift between starter-kit defaults and product baseline | tooling | ✅ |
| [#66](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/66) | v0.4.0 `make validate` silently skips lint/typecheck/test gates | tooling | ✅ |

## Post-roadmap fixes (July 2026)

Governance-hardening batch discovered after the v0.7.x release
series. All close tracked issues.

| Issue | PR | Title | Area | Status |
| --- | --- | --- | --- | --- |
| [#102](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/102) | [#112](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/112) | Enforce CRIT-008 at the git layer; agent-layer hook as defense-in-depth | hooks | ✅ |
| [#103](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/103) | [#113](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/113) | `--gate audit` lookup dead: accept both `rule` string and `rules` list | tooling | ✅ |
| [#104](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/104) | [#118](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/118) | CRIT-002 gate passed vacuously when the governance loader crashed (process-substitution masked the exit code) | tooling | ✅ |
| [#108](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/108) | [#123](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/123) | Eliminate `governance_review` false negatives for rule-data drift, malformed traceability, invalid UTF-8, empty YAML, and structural hook registration | governance | ✅ |
| [#105](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/105) | [#121](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/121) | `test-typescript` swallowed a failing `node --test` exit code (`\|\| echo` bound to the whole `&&` chain), so a red JS suite passed `make test` / `make validate`; rewritten with a three-way `find` guard (scan error → loud failure, no matches → WARN + exit 0, matches → run and propagate) | ci / tooling | ✅ |
| [#106](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/106) | [#126](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/126) | `npm test` on fresh scaffolds ran `vitest run` whose include glob never matched the template's node:test suites; repointed at `node --test` with recursive globs, dropped unused vitest devDependencies, fixed `test-typescript`'s missed `test_*.cjs` | tooling | ✅ |
| [#107](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/107) | [#128](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/128) | devcontainer `post-create.sh` robustness: `ensure_uv` logged false success when the `curl \| sh` pipeline failed (no pipefail); curl missing from the `pkg_bin` apt map despite the comment's promise; unguarded `npm config set prefix` could abort the script under `set -eu` | tooling | ✅ |
| [#109](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/109) | [#130](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/130) | Shell validation scripts correctness & portability: unquoted `compgen -G` suppressed drift errors for globs with spaces; frontmatter checks grepped the whole file instead of the `--- ... ---` block; unescaped `.` in the action-pin skip prefix exempted single-char-owner actions; `rg`-vs-`grep` marker-scan divergence pinned to one semantic (`rg --no-ignore --hidden`); `check-doc-drift.sh` no longer self-disables on macOS bash 3.2 (`sort -u` dedupe replaces the associative array); `generate-sbom.sh` writes to a temp file and `mv`s on success instead of leaving a truncated SBOM; plus a Critic-found bash 3.2 frontmatter/SIGPIPE fix | tooling | ✅ |
| [#110](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/110) | [#132](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/132) | Template pruning correctness: orphaned `test_audit_hooks` twins shipped to the wrong language path (unused `.cjs` on python renders, dead `.py` on typescript) now pruned in both the cookiecutter hook and the copier `_tasks` mirror; the dead `docs/sbom-policy.md` prune entry resolved by authoring the planned CycloneDX SBOM generation/review policy (GAP-022/044 → landed); typo'd/unknown variant sentinel keys and nested/unbalanced `# variant:` blocks now raise `VariantError` instead of silently dropping content or corrupting the pruned `pyproject.toml`, with a shared-fixture unit suite exercising both duplicated parser copies | tooling | ✅ |
| [#133](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/133) | [#136](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/136) | Copier renders aborted because `_envops`'s `[#` comment-start (added to protect bash `${#arr[@]}`) collided with markdown `[#NNN]` issue-links; escaped the three offending links to `[issue #NNN]` (renders identically under both tools) with a `tests/` regression guard. Shipped alongside a **local CI** (`scripts/local-ci/`) standing in for billing-locked Actions — three tiers: host gate (`make local-ci`), OrbStack render matrix (`make ci-orb`), advisory two-model Ollama review (`make review`) | tooling | ✅ |
| [#135](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/135) | [#138](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/138) | Rendered-project `make validate` failures in a clean CI container (first surfaced by the new local CI's `RUN_VALIDATE=1` mode; billing-locked Actions never ran these gates): `test_validation_scripts.py`'s sbom test copied `scripts/generate-sbom.sh` without gating on `include_sbom` (the script is pruned for `include_sbom=no`) → `FileNotFoundError`, now `@unittest.skipUnless((SCRIPTS/"generate-sbom.sh").exists())`; the two `post-create.sh` AI-CLI tests failed because `ensure_uv`'s sole unguarded `mktemp` aborted the script under their stub-only PATH → guarded with `command -v mktemp` (the `sudo` calls were already `if !`-guarded); the governance body-only-agent-key test triaged as already fixed by #130. Shipped via the ADWS pipeline (PROMOTE, 7/7 gates) | tooling | ✅ |
| [#119](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/119) | [#140](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/140) | CRIT-001 `marker-scan.sh` vacuous-scan follow-up to #104: the `--list-marker-surfaces` read used an unguarded `done < <("${GOV_LOADER[@]}" ...)` process substitution, so under `set -euo pipefail` a governance-loader crash specific to that call (after `--marker-regex` had already succeeded) silently left `surfaces` empty and the scan proceeded against zero surfaces instead of failing. Replaced with the same capture-first `if ! surfaces_raw="$(...)"` guard + `<<<` here-string as `check-governance.sh` (bash 3.2-safe); added a regression test (`surfaces: null` fixture asserting non-zero exit **and** `governance loader failed` on stderr, proven non-tautological against the pre-fix script); corrected the now-stale `check-governance.sh` cross-reference comment. Shipped via the ADWS pipeline (PROMOTE with warnings, 7/7 gates, exit 10) | tooling | ✅ |
| [#111](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/111) | [#148](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/148) | Refactoring & optimization epic — five remaining items (#1 coverage-theater and #2 triplicated-prune sync-test were already resolved by #110/#132; verified, untouched): **#3** governance-loader fan-out collapsed to one `--emit` call per script (~6→2 interpreter starts per `make validate`); **#4** shared `read_lines_into_array` helper across the five check scripts + `check-traceability.sh` triple-`jq`→single pass; **#5** dead `check_tool`/`check_file` `defs.mk` macros removed, the parsed-but-unread `--list` flag **wired** to actually list (keeps `query-governance.sh --list` working) rather than deleted, `RECOMMENDED (4)`→`(3)` yaml count comment; **#6** `governance_review/__main__.py`'s module-level `raise SystemExit(main())` guarded behind `if __name__`; **#7** copier `_tasks` deletions made Windows-portable (YAML-list `python`, no `rm`/`find`), `.gitkeep` sweep no longer traverses `.git`. Field-multiplexing hardened to preserve embedded tabs / loud-fail on embedded newlines at both the `--emit` and `check-traceability.sh` sites; the empty-array `"${arr[@]}"` expansion guarded (`${arr[@]+…}`) for macOS bash 3.2 — a real empty-list crash caught in Mac validation that the Linux/bash-5 pipeline is structurally blind to. Shipped via the ADWS pipeline (job_20260720_0001, PROMOTE 7/7 gates, consensus 2 rounds clean, grader 6/6) + operator bash-3.2 fix | tooling | ✅ |

> Follow-up filed during the #118 review:
> [#119](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/119)
> — `marker-scan.sh` retained an unguarded `done < <(...)` read for
> `--list-marker-surfaces` with a milder instance of the same
> vacuous-pass risk. **Resolved in
> [#140](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/140)**
> — same capture-first guard as `check-governance.sh`, with a
> regression test.

> Follow-up filed during the #105 work:
> [#122](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/122)
> — the `pipefail`/`find`-traversal-error residual in the first-cut
> fix. Independently flagged by CodeRabbit at PR review and hardened
> directly in #121 (three-way `find` guard), so #122 closed with the
> merge rather than becoming standalone backlog.

> The broader v0.7.x release-hardening batch (#87–#101: CI action
> pinning, dev-container compatibility, THREAT_MODEL drift, CHANGELOG
> seeding, slash-command de-prefixing) is recorded per-version in the
> root [`CHANGELOG.md`](../CHANGELOG.md) rather than re-tabled here.

## Sprint tracking

Project #6 carries a `Sprint` single-select field with these slots:

| Slot | Window |
| --- | --- |
| Backlog | unscheduled |
| Sprint 1 | 2026-05-06 → 2026-05-19 |
| Sprint 2 | 2026-05-20 → 2026-06-02 |
| Sprint 3 | 2026-06-03 → 2026-06-16 |
| Sprint 4 | 2026-06-17 → 2026-06-30 |
| Future | beyond Sprint 4 |

When new work is filed, add it to Project #6, set `Sprint: Backlog`,
fill `Effort` and `Leverage`, and pull into the active sprint when
planning.

---

## Refresh

This file is updated manually as issues complete. To regenerate the
status column from the live GitHub project:

```sh
gh project item-list 6 --owner Org-EthereaLogic --format json \
  --jq '.items[] | {issue: (.content.url // empty), status: .status}'
```

When closing an issue locally, also update the matching row's status
emoji here and commit alongside the implementation change. The
authoritative source remains the GitHub project; this dashboard's
job is to be readable from the repo at a glance.

## Provenance

- Created: 2026-05-02
- Source: research report and improvement plan in conversation
- Updated 2026-05-06: post-roadmap fix issues (#38–45, #66) added to
  the GitHub project; `Sprint` field and `Deferred` status option
  added to Project #6.
- Updated 2026-05-06: optimization-roadmap follow-on items filed
  as #69–#74 against Project #6 (`Sprint: Backlog`); shipped items
  from `docs/OPTIMIZATION_ROADMAP.md` (#1–#4, #6, #7) annotated
  with status notes inline in that doc.
- Updated 2026-07-18 (post-merge sync): current-state advanced from
  2026-05-06 to 2026-07-18; recorded the July governance-hardening
  fixes (#102/#112, #103/#113) and referenced the v0.7.x batch
  (#87–#101) to the root CHANGELOG. Workspace hygiene in the same
  sync: pruned two merged worktrees/branches
  (`claude/code-review-ultra-1a5298`,
  `claude/crit-008-hook-bypass-77710f`) and cleared ADWS scratch
  (`_adws_tmp/`, `artifacts/`). `--gate audit` / `--gate hooks_test`
  / `--gate nonexistent` and the governance-loader suite (15 tests)
  verified green on `main` before recording.
- Updated 2026-07-18 (second post-merge sync): recorded
  [#115](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/115)
  (pins `rules`-over-`rule` precedence for both-keys gate entries;
  governance-loader suite now 16 tests), closing out the #103 review
  feedback. Both feature branches deleted local+remote after merge.
  Operational note: GitHub Actions is currently locked by an org
  billing issue — every workflow run (incl. CodeQL) fails at job
  start until billing is resolved; merges in this batch were gated
  on local validation instead.
- Updated 2026-07-18 (third post-merge sync): recorded
  [#104](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/104)/[#118](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/118)
  (guards all four governance-loader reads in `check-governance.sh`
  with capture-first `if ! var="$(...)"` so a loader crash fails
  loudly instead of vacuously passing CRIT-002; adds a corrupt-rules
  regression test). Review of #118 corrected an over-claim about
  `marker-scan.sh` and filed follow-up
  [#119](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/119)
  for the same-class risk there. Workspace hygiene in the same sync:
  cleared local ADWS scratch (`_to_delete/`, `artifacts/`) and
  deleted the merged branch local+remote. Validated locally (healthy
  path exit 0; corrupt-YAML path exit 1 with diagnostic and no
  vacuous OK; `test_skill_contracts.py -k governance` 4/4) — GitHub
  Actions remains billing-locked, so the merge was gated on local
  validation as with #115.
- Updated 2026-07-18 (fourth post-merge sync): recorded
  [#108](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/108)/[#123](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/123)
  and its review-fix commit. The merged validator now reads shared
  enforcement data from `governance-rules.yaml`, reports malformed
  inputs explicitly, scans through invalid UTF-8, and validates the
  complete `PreToolUse:Bash` command-hook structure. Codacy's 20
  pytest-assert false positives were suppressed at the exact test
  lines and all five new complexity findings were refactored below
  threshold; Codacy reanalysis passed. Fresh post-merge Linux/Bash 5
  validation passed 126 rendered tests and all `make validate` gates.
  GitHub-hosted Actions and Copilot review remained unable to
  start because the organization account is billing-locked. Workspace
  hygiene removed the merged #123 worktree and local branch and
  pruned its already-deleted remote-tracking ref. Live issue refresh
  also corrected #69–#74 from stale backlog entries to completed and
  identified #105–#111, #119, and #122 as the current open follow-on
  queue. Project-field refresh was not run because the current GitHub
  token lacks `read:project`.
- Updated 2026-07-18 (fifth post-merge sync): recorded
  [#105](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/105)/[#121](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/121)
  — the `test-typescript` recipe swallowed a failing `node --test`
  exit code (`|| echo` bound to the whole `&&` chain), so a red JS
  suite passed `make test`/`make validate`. Fixed with a three-way
  `find` guard: a scan error fails loud (`ERROR` + non-zero exit), no
  matching files → WARN + exit 0, and matches run
  `find … -exec node --test {} +` (propagating a real failure).
  Produced end-to-end through the ADWS pipeline (PROMOTE, 7/7 gates).
  Follow-up
  [#122](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/122)
  (the residual's `pipefail`/`find`-error variant) was filed, then
  independently flagged by CodeRabbit at PR review and hardened in the
  same PR — so it closed with #121 rather than becoming backlog.
  Validated locally by rendering the template and driving
  `make test-typescript` across the failing / no-files / passing /
  `*.test.cjs` / unreadable-`tests/`-subdir cases (exit 2 / 0 / 0 / 0 /
  2); GitHub Actions remains billing-locked, so the merge was gated on
  local validation as with the prior batches. Open follow-on queue
  refreshed to #106, #107, #109, #110, #111, #119.
- Updated 2026-07-18 (sixth post-merge sync): recorded
  [#106](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/106)/[#126](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/126)
  — `npm test` on a fresh scaffold ran `vitest run`, whose default
  include glob never matches the template's node:test suites
  (`tests/test_*.js` / `test_*.cjs`), failing with "No test files
  found" while `make test` passed. Fixed by pointing
  `test`/`test:watch`/`coverage` at `node --test` with quoted
  recursive `'tests/**/…'` globs (expanded by Node's own glob engine,
  matching the Makefile `find`'s recursion) and dropping the unused,
  version-mismatched vitest devDependencies. The fix uncovered and
  closed a second latent gap: the `test-typescript` recipe's `find`
  patterns missed `test_*.cjs`, so `make test` had silently skipped
  `tests/test_audit_hooks.cjs`. Docs aligned end-to-end (READMEs,
  QUICKSTART-TYPESCRIPT with an exact runner-equivalence statement
  incl. the dot-directory caveat, cookiecutter.json prompt text,
  scaffold agent docs, BUILD_PLAN, EXAMPLES, OPTIMIZATION_ROADMAP).
  Produced end-to-end through the ADWS pipeline as two gated jobs
  (job_20260718_0006 PROMOTE-with-warnings; audit-driven follow-up
  job_20260718_0007 PROMOTE, drift-grader 4/4 satisfied), with an
  independent post-promote audit between them whose findings
  (top-level-only npm globs vs recursive `find`; an overclaiming
  Quickstart equivalence sentence; residual operational vitest
  references) were all resolved in the second commit; evidence trees
  retained at `artifacts/job_20260718_000{6,7}/`. Validated locally
  pre-merge on rendered typescript + polyglot scaffolds (49/49 both
  runners; injected failing top-level and nested tests exit non-zero
  under both) and spot-checked post-merge on `main` (render + both
  runners green). GitHub Actions remains billing-locked (all jobs
  fail at start with 0 steps, incl. on `main`), so the merge was
  gated on local validation as with the prior batches. Workspace
  hygiene in the same sync: merged branch deleted local+remote with
  its stale remote-tracking ref pruned, ADWS transfer scratch
  (`_to_delete/`) removed, and the stale zero-byte `.git/index.lock`
  (held open read-only by a desktop app, no live git process)
  removed per the F-10 checklist before applying the patches.
- Updated 2026-07-19 (seventh post-merge sync): recorded
  [#107](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/107)/[#128](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/128)
  — three related robustness bugs in the template's devcontainer
  `post-create.sh`: `ensure_uv` logged "uv installed" even when the
  `curl \| sh` pipeline failed (`set -eu` without `pipefail` let an
  empty-stdin `sh` exit 0), now fixed by downloading the installer to
  a temp file, checking curl's own exit status, and gating the
  success log on `command -v uv`; `[curl]=curl` added to the
  `pkg_bin` apt map so the network-probe comment's "apt step will
  install curl" promise is actually kept on minimal images; and
  `npm config set prefix` plus its `mkdir -p` guarded with `\|\| log`
  so a read-only npmrc can no longer abort the whole script,
  preserving the "never fails the container build" contract.
  Produced end-to-end through the ADWS pipeline (job_20260719_0001,
  patch mode, clean PROMOTE, drift-grader 4/4 satisfied) — first run
  orchestrated from the standalone `adws-pipeline-skill` workflow
  rather than the in-repo copy; evidence tree retained at
  `artifacts/job_20260719_0001/`. Validated locally pre-merge:
  template pytest suite 26 passed; rendered typescript scaffold
  `npm test` 49/49; `bash -n` + shellcheck clean on the modified
  script (no new findings vs baseline). GitHub Actions remains
  billing-locked, so the merge was gated on local validation as with
  the prior batches. This sync also backfills the #106/#126 row the
  sixth sync omitted from the July fixes table. Workspace hygiene:
  merged `adws/job_20260719_0001/…` branch deleted local+remote with
  its remote-tracking ref pruned.
- Updated 2026-07-19 (eighth post-merge sync): recorded
  [#109](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/109)/[#130](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/130)
  — six correctness/portability fixes across the shell validation
  scripts (quoted `compgen -G` glob resolution in
  `check-traceability.sh`; frontmatter checks in
  `check-governance.sh` constrained to the first `--- ... ---`
  block; escaped action-pin skip prefix in `check-action-pins.sh`;
  marker-scan search semantics pinned to `rg --no-ignore --hidden`
  parity in `lib/common.sh`; `check-doc-drift.sh` bash-3.2-portable
  dedupe so the gate no longer self-disables on macOS;
  `generate-sbom.sh` temp-file + `mv` so failures cannot leave a
  truncated SBOM), plus a Critic-found bash 3.2 frontmatter/SIGPIPE
  fix, all with a new focused regression suite
  (`tests/test_validation_scripts.py`, incl. a 200,000-line bash 3.2
  regression). Produced through the ADWS pipeline
  (job_20260718_0008): the initial run terminated
  RETRY/TEST_GATE_FAILURE (execution report retained at
  `artifacts/job_20260718_0008/`); the retry fixed the two real gate
  blockers (ruff import order; the marker-fallback fixture's
  `python3` symlink broke venv resolution and dropped PyYAML — now
  an interpreter shim script) and confirmed the remaining 31
  template-test failures byte-identical on `main` (pre-existing
  macOS-env failures; the branch adds 8 newly passing tests, 0 new
  failures). Review feedback resolved pre-merge: Codacy's 20 new
  findings were bandit/semgrep noise on `subprocess.run` in the test
  file (suppressed per repo `# nosec`/`# nosemgrep` convention,
  Codacy green); CodeRabbit's two nitpicks applied (`git init` in
  the marker-scan fixture so `.gitignore` scoping is genuinely
  exercised; `B607` added to the git-init nosec). Validated locally
  pre-merge (Actions still billing-locked): new suite 4/4, rendered
  typescript scaffold `npm test` 49/49, `ruff check` clean.
  Workspace hygiene: ADWS worktree removed and merged
  `adws/job_20260718_0008/…` branch deleted local+remote.
- Updated 2026-07-19 (ninth post-merge sync): recorded
  [#110](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/110)/[#132](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/132)
  — the four template-pruning correctness gaps. (1) The orphaned
  `test_audit_hooks` twins: a python render shipped an unused
  `tests/test_audit_hooks.cjs` and a typescript render a dead `.py`
  (nothing in `hooks.mk` ran the off-language twin), now pruned in
  both the cookiecutter hook (`prune_language_files`) and the copier
  `_tasks` mirror, with `LANGUAGE_MATRIX` extended to cover them. (2)
  The dead `docs/sbom-policy.md` prune entry, resolved by authoring
  the planned CycloneDX SBOM generation/review policy doc (GAP-022 and
  GAP-044 flipped `planned` → `landed`; the entry becomes meaningful
  and the `SECURITY.md`/`generate-sbom.sh` references now resolve). (3)
  and (4) Two silent-corruption classes in the `# variant:` sentinel
  parser — unknown/typo'd keys (previously dropped content from *every*
  render) and nested/unbalanced blocks (could leak marker lines into
  the pruned `pyproject.toml`) — now raise `VariantError`. The parser
  fix landed identically in both duplicated copies
  (`hooks/_prune_pyproject.py` for copier, `hooks/post_gen_project.py`
  for cookiecutter), guarded by a new shared-fixture suite
  (`tests/test_prune_variants.py`, 50 cases run against both copies).
  Review feedback resolved pre-merge: CodeRabbit's MD040
  fenced-block-language nitpick applied; Codacy's 11 findings were
  bandit `B101` `assert` noise in the new test file (suppressed per the
  repo `# nosec B101` convention) plus one pyright pytest-import false
  positive. Validated locally pre-merge (Actions billing-locked, so no
  green CI): full pytest suite 76 passed on 3.12; cookiecutter renders
  confirm twin pruning and sbom-policy shipping/pruning across
  python/typescript/polyglot; the copier prune script CLI prunes
  correctly and exits non-zero with `VariantError` on a typo'd key.
  Filed during verification:
  [#133](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/133)
  — a pre-existing bug where copier's `_envops` `[#` comment-start
  (added to protect `${#arr[@]}` in shell scripts) collides with the
  markdown link `[#102]` at `DIRECTIVES.md:184`, aborting every copier
  render and reddening the whole `template-smoke-test` workflow on
  `main` (independent of this change; also compounded by the
  billing-locked Actions account). Workspace hygiene: PR branch deleted
  local+remote on squash-merge with stale remote-tracking refs pruned;
  throwaway caches (`.pytest_cache`, `__pycache__`, `.coverage`)
  cleared; the 294 MB gitignored `artifacts/` ADWS evidence tree left
  intact (prior syncs reference it as retained evidence).
- Updated 2026-07-19 (tenth post-merge sync): shipped
  [#133](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/133)/[#136](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/136)
  — escaped the `[#102]` markdown links (`DIRECTIVES.md`,
  `.claude/hooks/README.md`) that collided with copier's `[#`
  comment-start, so copier renders again and cookiecutter↔copier
  equivalence holds; guarded by
  `tests/test_no_copier_comment_collision.py`. Landed together with a
  **local CI** (`scripts/local-ci/`) standing in for the
  billing-locked GitHub Actions: Tier 1 `make local-ci` (host `pytest
  tests/` on Py 3.12 via uv + a default render smoke); Tier 2 `make
  ci-orb` (7-variant cookiecutter+copier render matrix +
  render-equivalence in a `python:3.12-bookworm` OrbStack container,
  rendering from a clean shallow clone of HEAD to dodge the untracked
  `artifacts/` nested-repo tree that trips copier's dirty-tree
  handling; `RUN_VALIDATE=1` opt-in also runs each render's `make
  validate`); Tier 3 `make review` (advisory two-model Ollama review —
  `gpt-oss:120b` deep + `qwen3.5:9b` fast — of the branch diff, never
  blocking). Evidence is append-only JSONL in gitignored `ci_logs/`.
  Verified locally (Actions billing-locked): Tier 1 green (77 pytest +
  smoke); Tier 2 default all 16 legs green (all 7 variants × both tools
  + render-equivalence); Tier 2 `RUN_VALIDATE=1` honestly fails on a
  pre-existing rendered-test bug (the fail-fast masking was found and
  fixed — a subshell `set -e` is suppressed under `|| st=fail`, so an
  `&&` chain is used instead); Tier 3 produced a real review with
  correct Ollama-down (exit 3) / model-missing (skip) handling. Filed
  [#135](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/135):
  the Tier-2 full-validate mode caught a pre-existing template-test bug
  that billing-locked cloud CI never ran —
  `test_validation_scripts.py`'s sbom test references
  `scripts/generate-sbom.sh` without gating on `include_sbom` (pruned
  for `include_sbom=no`), plus three failures to triage. Surfaced (not
  committed): repo-root `.env` holds a live-looking GitHub PAT in
  cleartext — rotate if real. Workspace hygiene: PR branch deleted
  local+remote on squash-merge, refs pruned; the 294 MB gitignored
  `artifacts/` tree left intact.
- Updated 2026-07-19 (eleventh post-merge sync): shipped
  [#135](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/135)/[#138](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/138)
  — the first fix driven by the new local CI's Tier-2
  `RUN_VALIDATE=1` findings, run end-to-end through the ADWS pipeline
  (`job_20260719_0002`, patch → PROMOTE, exit 0; 7/7 gates on first
  attempt, consensus clean both rounds, grader 4/4, zero rewinds/parse
  failures). Gated `test_validation_scripts.py`'s sbom test on
  `generate-sbom.sh` presence (`skipUnless` — skipped, not
  `FileNotFoundError`, on `include_sbom=no`; still runs on `=yes`);
  guarded `ensure_uv`'s sole unguarded `mktemp` in `post-create.sh`
  (the real exit-127 crash under the two AI-CLI tests' stub-only PATH —
  the `sudo` calls were already `if !`-guarded); triaged the governance
  body-only-agent-key test as already resolved by #130 (awk scoped to
  the first `--- ... ---` fence) — documented, no code change.
  Validation: rendered `python-mit-ty` (`include_sbom=no`) under Py
  3.12 = 133 passed, 1 skipped, 0 failed (baseline 3 failed); macOS
  failure-set parity confirmed vs `main` — the two post-create tests
  stay red on both from a pre-existing bash-3.2 `declare -A`
  incompatibility at `post-create.sh:57` (`jq` unbound), out of #135's
  scope and a follow-up candidate. Codacy 0 issues, CodeRabbit no
  actionable comments (5/5 pre-merge checks), Copilot billing-locked;
  merged with `--admin` over billing-locked Actions. Branch deleted
  local+remote; `artifacts/` evidence tree intact.
- Updated 2026-07-19 (twelfth post-merge sync): shipped
  [#119](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/119)/[#140](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/140)
  — the CRIT-001 `marker-scan.sh` vacuous-scan follow-up filed during
  the #104/#118 review, run end-to-end through the ADWS pipeline
  (`job_20260719_0003`, patch → PROMOTE with warnings, exit 10; 7/7
  gates on first attempt, 9/9 validators pass, consensus clean both
  rounds, grader 3/4 satisfied + 1 partial, zero rewinds/parse
  failures). Replaced the unguarded
  `done < <("${GOV_LOADER[@]}" --list-marker-surfaces)` read with the
  same capture-first `if ! surfaces_raw="$(...)"` guard + `<<<`
  here-string as `check-governance.sh` — a loader crash on that call
  now exits non-zero with a named diagnostic instead of scanning zero
  surfaces; added a `surfaces: null` regression test (asserts non-zero
  exit + `governance loader failed`, proven non-tautological against
  the pre-fix script); corrected the now-stale `check-governance.sh`
  cross-reference comment. Validation: full `test_validation_scripts.py`
  suite 5/5 on both Linux (bash 5.2) and macOS (bash 3.2.57);
  `marker-scan.sh` still exits 0 on the real `governance-rules.yaml`.
  The single grader warning is AC3's runtime assertions being
  ungradeable from the static diff alone (proven in the test-phase
  evidence). Merged with `--admin` over billing-locked Actions; branch
  deleted local+remote; `artifacts/` evidence tree intact.
- Updated 2026-07-19 (thirteenth post-merge sync): shipped
  [#142](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/142)
  — a docs-only follow-up to the #119/#140 merge. The `#104` CHANGELOG
  entry's parenthetical still recorded that `marker-scan.sh` "retains an
  unguarded `done < <(...)` read for `--list-marker-surfaces` ... tracked
  separately", which #140 superseded. Appended a forward pointer to the
  `#119` entry rather than rewriting the parenthetical — the changelog is
  an append-only record of what was true at each release, so correcting
  the historical claim in place would erase accurate history. No issue
  filed; no source or template change. Validation: `tests/` 77 passed
  (the 26 initial failures were a missing `cookiecutter` dep in the local
  env, not the diff). Review: the two `make review` models split on
  whether the literal `[#119]` link re-triggers the #133 copier
  comment-delimiter collision — resolved against the flagging model, since
  `copier.yml` sets `_subdirectory: {{cookiecutter.project_slug}}` so the
  root `CHANGELOG.md` is never rendered (which is why
  `test_no_copier_comment_collision.py` deliberately scans only
  `TEMPLATE_ROOT`), confirmed empirically by a `copier copy --vcs-ref=HEAD`
  render at `552ccdb` succeeding with exit 0. Its suggested `[[#119]]`
  escape would have corrupted a working link to guard a non-existent
  render path; adjudication recorded as a PR comment. The #133 collision
  stays live for any `[#` added **under** `{{cookiecutter.project_slug}}/`.
  Codacy 0 issues, CodeRabbit no actionable comments, Copilot
  billing-locked; merged by plain squash (no `--admin` needed — the
  billing-locked Actions are not required checks). Branch deleted
  local+remote. Housekeeping: pruned four stale remote-tracking refs
  (`docs/dashboard-sync-pr140`, `docs/sync-dashboard-issue135`,
  `fix/issue-119-marker-scan-surfaces-guard`, `fix/issue-135-validate-clean-ci`)
  already deleted on the remote; no untracked files present, and the
  locally-excluded `artifacts/` evidence tree was left intact.
- Updated 2026-07-19 (fourteenth post-merge sync): shipped
  [#145](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/145)
  — **adopted the local CI as the repo's gate** rather than a tool one
  person happened to run. `.githooks/pre-push` is now **tracked** (it was
  generated into an untracked file, so the gate existed on exactly one
  machine); `make install-hooks` points `core.hooksPath` at `.githooks`
  and chmods the tracked hook, mirroring the `make hooks-install`
  convention the template already ships to generated projects, so one
  command wires a fresh clone. `AGENTS.md` gains a **Local CI (interim
  gate)** section stating the policy — `install-hooks` once per clone,
  Tier 1 fires automatically on every push, `make ci-orb` before merging,
  `make review` advisory only, paste the JSONL evidence into the PR body —
  cross-referenced from *Workflow*. Dogfooded on its own PR: the pre-push
  hook fired for real on `git push` (pytest 7s + render smoke, PASS) and
  `make ci-orb` was green (all 7 variants × both tools + equivalence,
  13s). Also re-checked the deep gate now that
  [#138](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/138)
  landed: `RUN_VALIDATE=1` went from four failures to **one**, so
  `scripts/local-ci/README.md` was refreshed and the residual filed as
  [#144](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/144)
  — `test_governance_check_rejects_body_only_agent_key` exits red on Linux.
  Follow-up verification corrected the initial diagnosis: Linux render order
  returns `.claude/agents/README.md` first, the test selected that file, and
  `check-governance.sh` correctly skipped it. Selecting a real agent definition
  proves the validator rejects the body-only key, so #144 is a deterministic
  test-selection fix rather than another CRIT-002 vacuous-pass defect. The full
  deep-matrix rerun then exposed a separate root-owned npm-cache failure in the
  TypeScript and polyglot legs, tracked as #147. Independent testing of both
  fixes upheld dissent because six `ty` legs then rejected the two PR #148
  `pytest.skip(reason=...)` calls. A first positional-message correction
  preserved runtime behavior but `ty` rejected that form too. Moving the same
  conditions and messages to `@pytest.mark.skipif` decorators uses an accepted
  pattern without weakening validation. Workspace hygiene: PR branch deleted
  local+remote on
  squash-merge with refs pruned; `artifacts/` left intact.
- Updated 2026-07-20 (fifteenth post-merge sync): shipped
  [#148](https://github.com/Org-EthereaLogic/agentic-starter-kit/pull/148)
  — issue #111's five remaining cleanup items (#3 governance-loader fan-out
  `--emit`; #4 `read_lines_into_array` helper + `check-traceability.sh`
  single-`jq`-pass; #5 dead `defs.mk` macros removed, `--list` **wired** not
  deleted, `RECOMMENDED` yaml count comment; #6 `__main__` import guard; #7
  copier `_tasks` Windows portability). #111's #1/#2 were already resolved
  by #110/#132 (verified, untouched). Produced by the ADWS pipeline: two
  jobs ended **RETRY** when the Critic caught real regressions the tester
  missed (deleting `--list` broke the shipped `query-governance.sh --list`;
  a `check-traceability.sh` embedded-newline value silently dropped) before
  job_20260720_0001 reached a clean **PROMOTE** (7/7 gates, consensus 2
  rounds clean, grader 6/6). **Mac-side validation then caught a macOS
  bash-3.2 regression the Linux/bash-5 container is structurally blind to**:
  empty `read_lines_into_array` arrays expanded as `"${arr[@]}"` abort under
  `set -u` on bash 3.2 (a real crash on empty governance/traceability
  lists; baseline handled them) — guarded with `${arr[@]+"${arr[@]}"}` and
  re-validated on macOS (all 5 governance scripts byte-identical to baseline
  incl. empty-list cases; pytest failure-set parity with main, 0 new
  failures; TypeScript scaffold `npm test`). Merged by plain squash (main
  unprotected; billing-locked Actions are not required checks); CodeRabbit 0
  actionable, Copilot no comments, Codacy the repo-tolerated test-assert
  noise class + one soft complexity warning on the validated
  `emit_directive_listing`. Branch deleted local+remote; `artifacts/`
  evidence left intact. Observation (out of #111 scope, not changed):
  `docs/BRIEFING.md` documents four RECOMMENDED practices (REC-001..004)
  while `governance-rules.yaml` implements three (REC-001..003); #5
  corrected only the yaml's own count comment, leaving the briefing/yaml
  delta for a separate decision.
- Related memory: `peer_template_landscape.md` (May 2026 survey)
