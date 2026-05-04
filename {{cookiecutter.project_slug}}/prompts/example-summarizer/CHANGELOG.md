# example-summarizer — CHANGELOG

Append-only history of shipped versions for the `example-summarizer`
prompt. One row per version. Once a row is committed on
`{{ cookiecutter.default_branch_name }}` it is not edited; corrections
land as new rows.

## v1 — initial baseline

- **Date:** 2026-05-03
- **Owner:** {{ cookiecutter.author_name }}
- **Behavior:** Summarize a paragraph in one sentence (≤ 25 words).
- **Eval evidence:** `evals/promptfooconfig.yaml` (test
  `summarizer-keeps-key-noun`).
- **Rollback:** none — this is the first version.
- **Why:** Establish a working example so contributors have a
  template for the versioning convention without inventing one.
