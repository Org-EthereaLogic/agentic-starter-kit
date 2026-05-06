# Prompt Versioning Policy

> **SWEBOK anchor:** Software Maintenance KA §4.16 — configuration
> management of AI-generated and AI-consumed artifacts.
>
> **GAP closed:** GAP-036 — prompt versioning policy.

---

## 1. Scope

This policy covers every prompt that the project delivers to an LLM at
runtime: slash-command bodies (`.claude/commands/`), agent system
prompts (`.claude/agents/`), and application-layer prompts in
`prompts/`.

A *prompt* is a contract between the application and the LLM.
Changing it may alter observable outputs, break downstream parsers, or
shift model behavior in safety-relevant ways. It must be treated with
the same discipline as a public API change.

---

## 2. Storage convention

All versioned application prompts live under `prompts/` in the project
root.

```
prompts/
  README.md                  ← convention guide (this policy in short form)
  summarize-v1.0.md          ← initial version
  summarize-v2.0.md          ← non-breaking update
  extract-entities-v1.0.md
```

Each file carries YAML frontmatter:

```yaml
---
name: summarize
version: "2.0"
model: claude-sonnet-4-6
breaking: false
supersedes: summarize-v1.0.md
---
```

| Field | Required | Meaning |
| --- | --- | --- |
| `name` | yes | logical prompt identifier (stable across versions) |
| `version` | yes | semantic version string |
| `model` | yes | target model ID at authoring time |
| `breaking` | yes | `true` if callers must update before deploying |
| `supersedes` | no | filename of the previous version this replaces |

---

## 3. Versioning rules

Treat the major.minor version as a contract version:

| Change type | Version bump | `breaking` | Required actions |
| --- | --- | --- | --- |
| Formatting, typo, whitespace | patch (implicit) | `false` | Update file, re-run `make eval` |
| New optional instruction, clarification | minor | `false` | Update file, re-run `make eval` |
| Changed output structure or schema | major | `true` | New file, deprecate old, update callers, re-run `make eval` |
| Removed capability or narrowed scope | major | `true` | New file, deprecate old, update callers, update evals |
| Changed safety boundary or refusal behavior | major | `true` | ADR required before merge; security review per `SECURITY.md §3` |

---

## 4. Lifecycle

```
draft → review → active → deprecated → archived
```

1. **Draft** — authored in a branch, not called from production code.
2. **Review** — evaluated via `make eval`; threshold must pass.
3. **Active** — merged to default branch; referenced by callers.
4. **Deprecated** — superseded by a newer version; callers migrated.
   Keep the file for 90 days to allow rollback.
5. **Archived** — moved to `prompts/archive/` after the deprecation
   window; no longer called but retained for audit.

---

## 5. Eval gate

Every prompt in `prompts/` must have at least one test case in
`evals/promptfooconfig.yaml`. The `make eval` gate runs these tests and
exits non-zero if the pass rate falls below the configured threshold.

`make validate` invokes `make eval` on every CI run. A prompt change
that causes a threshold breach blocks the merge.

---

## 6. Slash-command and agent prompts

`.claude/commands/` and `.claude/agents/` prompt bodies follow the same
versioning discipline, with one difference: because these files are
named by role (e.g., `review.md`, `lead-software-engineer.md`), version
metadata lives only in the YAML frontmatter (`version:` field). There is
no file-rename on update.

A **breaking** change to a slash-command or agent prompt requires an
entry in `specs/deep_specs/` (ADR or design note) before the change
lands.

---

## 7. Constitutional alignment

| Principle | Application |
| --- | --- |
| `P4` — Explicit failure | `make eval` exits non-zero on threshold breach; no silent prompt degradation |
| `P5` — Append-only evidence | eval run artifacts land in `report/` for audit |
| `P6` — Minimum footprint | prompts change only what is necessary; scope is constrained per directive review |
| `P8` — Risk-class autonomy | breaking prompt changes require human sign-off before merge |

Cross-reference `DIRECTIVES.md IMP-005` (change notification) and
`CRIT-001` (no stub markers in canonical surfaces including
`prompts/`).
