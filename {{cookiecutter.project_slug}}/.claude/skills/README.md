# `.claude/skills/` — progressive-disclosure capability packs

Skills are the third Layer-3 surface (alongside `agents/` and
`commands/`). Each skill is a single Markdown file with YAML
frontmatter declaring **when** the skill should be loaded and
**what** it teaches the agent to do.

Per the Linux Foundation `SKILL.md` spec adopted in
`docs/RESEARCH_FINDINGS.md` §3.2, the agent reads only the
frontmatter for every skill at session start. The full body loads
**only when the task touches a path that matches the skill's
`paths:` glob list**. This keeps the always-on context budget lean
while still making domain-specific guidance discoverable.

## Inventory

| Skill | Triggers when the agent edits… | Wraps |
| --- | --- | --- |
| `run-validate` | source, tests, scripts, governance prose | `make validate` execution discipline |
| `audit-trail-tail` | `report/audit.jsonl` or any audit-tooling source | reading the per-tool-call audit log without leaking sensitive context |
| `traceability-update` | `specs/traceability.json` or its schema | safe edits to the traceability matrix that survive `make check-traceability` |

## Frontmatter contract

Every skill in this directory declares:

```yaml
---
name: <kebab-case skill id, must equal the filename without .md>
description: <one sentence — used by the loader to decide relevance>
paths:
  - <glob>          # any working-tree path; relative to project root
  - <glob>
---
```

The `paths:` list is a disjunction. The skill loads when the agent
intends to read or write **any** path matching **any** entry. Globs
follow standard shell semantics (`**` for recursive descent, `*`
for a single path segment).

Keep `description` under 200 characters. The loader uses it to
break ties when multiple skills are eligible; long descriptions
inflate the always-on context.

## Adding a new skill

1. Pick a kebab-case `name` that matches the filename
   (`my-skill.md` → `name: my-skill`).
2. Author a one-sentence `description` and a tight `paths:` list.
   Over-broad globs erode the progressive-disclosure benefit.
3. Body should be operational: when to invoke the skill, the
   exact command(s) it wraps, the failure modes the operator
   needs to know about, and the report format.
4. Add the skill to the inventory table above.
5. Re-run `make governance-check`. The check enforces that every
   `.md` in this directory carries `name`, `description`, and
   `paths:` frontmatter (Phase B3 onward).

## Coverage check

`scripts/check-governance.sh` verifies the three starter skills
listed above are present and well-formed. Renaming or deleting one
without updating the script is a `governance-check` failure.

## See also

- `../agents/README.md` — subagent inventory and contract.
- `../commands/` — slash-command inventory.
- `docs/RESEARCH_FINDINGS.md` §3.2 — the Linux Foundation
  `SKILL.md` spec this directory implements.
