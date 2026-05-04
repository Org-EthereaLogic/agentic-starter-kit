# prompts/ — Versioned LLM prompts

This directory holds the LLM prompts that ship as part of
{{ cookiecutter.project_name }}. Per `docs/prompt-versioning-policy.md`,
every prompt is a **contract** between the project and the model
provider: a change to the prompt is a change to the contract, and the
audit trail must show what changed and why.

## Layout

```
prompts/
└── <prompt-name>/
    ├── CHANGELOG.md   # version history (one row per shipped version)
    └── v<N>.md        # one file per shipped version (immutable)
```

- One **folder per prompt**. The folder name is the prompt's stable
  identifier; pick a short, hyphenated, scope-bearing name
  (`example-summarizer`, `triage-router`, `ticket-classifier`).
- One **file per shipped version** inside the folder. The filename
  matches a monotonically-increasing semver-major: `v1.md`, `v2.md`,
  `v3.md`. There is no `v1.1.md` — minor variants get folded into
  the next major when promoted.
- One **`CHANGELOG.md`** per prompt, recording the diff narrative for
  each version: what behavior changed, why, what eval evidence
  validated it, and what the rollback step is.

## Frontmatter

Every prompt file carries YAML frontmatter so eval tooling and
runtime loaders can discover it without parsing prose:

```yaml
---
name: <prompt-folder-name>     # must match the parent directory
version: v<N>                  # must match the filename
description: <one sentence summary>
owner: <github-handle or team>  # responsible reviewer for changes
---
```

Body content is plain Markdown. Use double-brace placeholders
({% raw %}`{{variable_name}}`{% endraw %}) for prompt variables — the same
syntax that `evals/promptfooconfig.yaml` resolves at evaluation time.

## Immutability

Once a `v<N>.md` is on `{{ cookiecutter.default_branch_name }}`,
**do not edit its semantic content**. Typo fixes that do not change
behavior are allowed (and noted in `CHANGELOG.md`); behavior changes
become `v<N+1>.md`. This is the same rule the `report/` directory
follows under `IMP-001` (append-only evidence).

## Adding a new prompt

1. Create `prompts/<new-name>/v1.md` with the frontmatter and body.
2. Create `prompts/<new-name>/CHANGELOG.md` with the v1 row.
3. Add at least one assertion-bearing test for the new prompt in
   `evals/promptfooconfig.yaml` so `make eval` exercises it.
4. Run `make eval` locally and confirm the gate is green.
5. Commit per `IMP-002` with scope `prompts`:
   `feat(prompts): add <new-name> v1`.

## Evaluating prompts

`make eval` runs `promptfoo` against every prompt referenced in
`evals/promptfooconfig.yaml`. The gate is enforced in CI by the
`eval` job in `.github/workflows/ci.yml`. A threshold breach (any
assertion failing under the configured threshold) is a non-zero
exit and blocks the PR.

## See also

- `docs/prompt-versioning-policy.md` — the canonical policy.
- `evals/README.md` — how the evaluation harness works.
- `DIRECTIVES.md` — `IMP-001` (append-only), `IMP-002` (commits).
