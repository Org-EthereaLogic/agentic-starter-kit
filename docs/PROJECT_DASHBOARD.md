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

The roadmap is divided into four phases. Each phase ends in a
publishable release. **Phase A → v0.2; Phase B → v0.3; Phase C →
v0.4.** Phase D is deferred polish.

| Phase | Name | Target | Issues | Total effort (days) |
| --- | --- | --- | --- | --- |
| A | Hardening | v0.2, due 2026-05-16 | 5 | 9 |
| B | Specialization | v0.3, due 2026-06-06 | 4 | 9 |
| C | Distribution | v0.4, due 2026-06-27 | 5 | 10 |
| D | Polish | deferred | 1 | 2 |

Status legend: 📋 Todo · 🟡 In Progress · ✅ Done · ⏸ Deferred

---

## Phase A — Hardening (v0.2, due 2026-05-16)

| ID | Issue | Title | Gap | Lev | Eff | Status |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | [#10](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/10) | OWASP Agentic Top 10 (2026) coverage matrix | G1 | High | 2 | ✅ |
| A2 | [#11](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/11) | Astral toolchain default (uv + ruff + ty) | G3 | Medium | 1 | ✅ |
| A3 | [#12](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/12) | Supply-chain hardening (SLSA + OSSF + audit + Macaron) | G4 | High | 3 | ✅ |
| A4 | [#13](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/13) | MCP server baseline + policy | G5 | Medium | 1 | ✅ |
| A5 | [#14](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/14) | Hook surface extension + audit trail | G7 | High | 2 | ✅ |

**Phase A gate:** `make validate` passes; OSSF Scorecards ≥ 7/10 on the rendered smoke project.

## Phase B — Specialization (v0.3, due 2026-06-06)

| ID | Issue | Title | Gap | Lev | Eff | Status |
| --- | --- | --- | --- | --- | --- | --- |
| B1 | [#15](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/15) | Author 8 specialized Claude Code agents | G10 | High | 3 | ✅ |
| B2 | [#16](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/16) | Author 16 slash commands with `/gov.*` prefix | G2, G10 | High | 3 | ✅ |
| B3 | [#17](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/17) | Add `.claude/skills/` with starter skills | G6 | Medium | 1 | ✅ |
| B4 | [#18](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/18) | `prompts/` + `evals/` + promptfoo + `make eval` | G2 | Medium | 2 | ✅ |

**Phase B gate:** every command/agent has YAML frontmatter; agents-coverage check in `make validate`; `/gov.*` ↔ `/speckit.*` mapping table complete.

## Phase C — Distribution (v0.4, due 2026-06-27)

| ID | Issue | Title | Gap | Lev | Eff | Status |
| --- | --- | --- | --- | --- | --- | --- |
| C1 | [#19](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/19) | Add `copier.yml` dual-mode template | G9 | High | 4 | 📋 |
| C2 | [#20](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/20) | `governance-review` CLI validator | G11 | Medium | 3 | 📋 |
| C3 | [#21](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/21) | Devcontainer + Dockerfile | G8 | Medium | 1 | 📋 |
| C4 | [#22](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/22) | MkDocs Material docs site (optional) | — | Low | 1 | 📋 |
| C5 | [#23](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/23) | Commitizen + release-please | G12 | Low | 1 | 📋 |

**Phase C gate:** a 6-month-old smoke project absorbs every Phase A/B/C addition via `copier update` without merge conflicts on locked governance files.

## Phase D — Polish (deferred)

| ID | Issue | Title | Gap | Lev | Eff | Status |
| --- | --- | --- | --- | --- | --- | --- |
| D1 | [#24](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/24) | Examples gallery / vignettes | — | Low | 2 | ⏸ |

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
- Related memory: `peer_template_landscape.md` (May 2026 survey)
