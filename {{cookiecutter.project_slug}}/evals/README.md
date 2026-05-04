# evals/ — Prompt evaluation gate

This directory holds the [promptfoo](https://promptfoo.dev) config
that exercises every shipped prompt under `prompts/`. The gate is
invoked locally via `make eval` and in CI via the `eval` job in
`.github/workflows/ci.yml`. A threshold breach (any assertion below
the configured threshold) is a non-zero exit and blocks the PR.

## What this does

- Loads each prompt referenced in `promptfooconfig.yaml`.
- Resolves variables (the {% raw %}`{{var_name}}`{% endraw %} tokens in
  prompt bodies) from each test's `vars` block.
- Sends the rendered prompt to the configured provider and runs the
  test's `assert:` rules against the response.
- Fails the run when the aggregate score for any test drops below
  the configured `threshold` (default `1.0` — every assertion must
  pass).

## The default provider

The shipped baseline uses promptfoo's built-in `echo` provider so
the gate is **hermetic** — no API keys are required and CI can run
without secrets. Echo returns the rendered prompt verbatim, which
is enough to verify the full pipeline:

- the prompt file resolves and parses
- variable interpolation works
- the eval harness invokes the provider
- assertions execute and the threshold gate enforces

When you are ready to evaluate against a real LLM, swap the
`providers:` block in `promptfooconfig.yaml` for your provider of
choice — `openai:gpt-4o-mini`, `anthropic:claude-haiku-4-5`,
`azureopenai:...`, or a custom JavaScript / Python provider. See
<https://promptfoo.dev/docs/providers/> for the full list.

## Running locally

```sh
make eval                    # runs the gate (npx fallback included)
```

If `promptfoo` is on `$PATH`, the Makefile uses it directly. If not
but `npx` is available (Node 20+), the Makefile pulls promptfoo
on demand. Install globally for faster repeat runs:

```sh
npm install -g promptfoo
```

## Adding tests

For each new prompt under `prompts/<name>/v<N>.md`:

1. Append a `prompts:` entry to `promptfooconfig.yaml`:
   ```yaml
   prompts:
     - file://../prompts/<name>/v<N>.md
   ```
2. Append a `tests:` entry with `vars:` for each {% raw %}`{{var}}`{% endraw %}
   in the prompt and an `assert:` block. Anchor each assertion to a stable
   property of the expected output (proper-noun preservation,
   length budget, regex match, etc.) — not a verbatim string.
3. Run `make eval` locally. The gate must be green before the PR
   merges.

## Test naming

Use a kebab-case `description:` prefix that reads as a one-line
contract: `<prompt-folder>-<property>`. Examples:

- `summarizer-keeps-key-noun`
- `triage-router-routes-billing-questions-to-billing-queue`
- `ticket-classifier-rejects-pii-leak`

## See also

- `docs/prompt-versioning-policy.md` — what counts as a prompt change.
- `prompts/README.md` — the versioning convention.
- `Makefile` — the `eval` target.
- <https://promptfoo.dev/docs/configuration/reference/> — config reference.
