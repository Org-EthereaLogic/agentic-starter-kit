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

**Current state (2026-07-18):** all roadmap work and the original
optimization set (#69–#74) are merged. The v0.7.x release-hardening
batch (#87–#101) and the July governance-hardening batch have also
shipped: #102/#112, #103/#113 with the #115 precedence-pin follow-up,
plus #104/#118 and #108/#123. The current follow-on queue is
[#105–#111, #119, and #122](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues?q=is%3Aopen+is%3Aissue),
covering test-gate correctness, devcontainer behavior, shell
portability, template pruning, and remaining governance-loader
robustness. Sprint 1 (2026-05-06 → 2026-05-19) was never populated
and its window has closed.

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

> Follow-up filed during the #118 review:
> [#119](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/119)
> — `marker-scan.sh` retains an unguarded `done < <(...)` read for
> `--list-marker-surfaces` with a milder instance of the same
> vacuous-pass risk (`Sprint: Backlog`).

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
- Related memory: `peer_template_landscape.md` (May 2026 survey)
