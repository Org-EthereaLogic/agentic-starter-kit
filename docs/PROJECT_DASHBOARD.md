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

**Current state (2026-05-06):** all roadmap and post-roadmap work is
merged. There are no open issues. The project board is ready to
receive the next sprint of work.

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
| B2 | [#16](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/16) | Author 16 slash commands with `/gov.*` prefix | G2, G10 | High | 3 | ✅ |
| B3 | [#17](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/17) | Add `.claude/skills/` with starter skills | G6 | Medium | 1 | ✅ |
| B4 | [#18](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/18) | `prompts/` + `evals/` + promptfoo + `make eval` | G2 | Medium | 2 | ✅ |

**Phase B gate:** every command/agent has YAML frontmatter; agents-coverage check in `make validate`; `/gov.*` ↔ `/speckit.*` mapping table complete.

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
- Related memory: `peer_template_landscape.md` (May 2026 survey)
