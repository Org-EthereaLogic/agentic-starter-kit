# prompts/

Application-layer prompts delivered to the LLM at runtime.

**Full policy:** `docs/prompt-versioning-policy.md`

## Quick reference

| Rule | Detail |
| --- | --- |
| One file per logical prompt + version | `{name}-v{major}.{minor}.md` |
| YAML frontmatter required | `name`, `version`, `model`, `breaking` |
| Every prompt needs an eval | Add a test case to `evals/promptfooconfig.yaml` |
| Breaking change → new file | Keep old file until all callers are migrated |
| Eval gate must pass | `make eval` before merging any prompt change |

## Frontmatter template

```yaml
---
name: my-prompt
version: "1.0"
model: claude-sonnet-4-6
breaking: false
---

Your prompt text here.
```

## Example

`prompts/summarize-v1.0.md` — initial summarization prompt.

Add your application prompts here following the convention above.
