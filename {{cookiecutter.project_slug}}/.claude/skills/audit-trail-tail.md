---
name: audit-trail-tail
description: "Tail and decode `report/audit.jsonl` — the per-tool-call event stream emitted by Layer-4 hooks — without leaking sensitive payloads back into chat."
paths:
  - "report/audit.jsonl"
  - "report/**"
  - ".claude/hooks/post-tool-use.cjs"
  - ".claude/hooks/session-start.cjs"
  - ".claude/hooks/user-prompt-submit.cjs"
  - "tests/test_audit_hooks.cjs"
---

# audit-trail-tail

Loads when the agent is about to read, write, or test the audit
trail. The trail is the append-only event stream that Layer-4
hooks (`session-start`, `user-prompt-submit`, `post-tool-use`)
write to `report/audit.jsonl` per Phase A5.

## Event shape

`report/audit.jsonl` is JSON Lines. Each line is one of:

| `type` | Emitter | Carries |
| --- | --- | --- |
| `session-start` | `session-start.cjs` | session boundary marker |
| `user-prompt` | `user-prompt-submit.cjs` | timestamp + SHA-256 hash of the prompt (never the prompt itself) |
| `tool-result` | `post-tool-use.cjs` | tool name, success bool, exit code, duration |

The hooks deliberately **do not** record tool inputs, tool
outputs, or prompt plaintext. Anything beyond the fields above
should be treated as a leak and filed as a finding against the
hook that produced it.

## Tail commands

```sh
# Last 20 events, pretty-printed
tail -n 20 report/audit.jsonl | jq .

# All tool failures in the current session
jq -c 'select(.type == "tool-result" and .success == false)' \
  report/audit.jsonl

# Tool-call duration histogram (rough; ms)
jq -r 'select(.type == "tool-result" and .duration_ms != null)
       | .duration_ms' report/audit.jsonl | sort -n | uniq -c
```

When the file is large, `tail -n` first; do not pipe the whole
log into chat. The audit trail grows append-only by design
(`IMP-001`); rotation is the operator's call, not the agent's.

## Reporting rules

- **Cite line numbers, not contents.** `report/audit.jsonl:412`
  beats pasting the JSON. The operator can replay the line; the
  agent cannot improve on the raw record.
- **Never edit the file.** It is append-only. Editing breaks
  forensic value and is a `CRIT-005` violation in spirit (PASS
  claims would no longer be replayable).
- **Treat absent `success` or `exit` as `unknown`, not `passed`.**
  Some upstream tools do not report exit codes.
- **Hash mismatches are a finding.** `user-prompt` records the
  SHA-256 of the prompt. If a downstream artifact references a
  prompt whose hash is not present in the trail, surface the gap.

## When to invoke

- After a `make validate` run, to confirm which tool calls
  actually executed.
- During incident triage, to reconstruct the agent timeline.
- When updating `.claude/hooks/post-tool-use.cjs` or its sibling
  hooks, to verify the new event shape is well-formed.
- Before merging a change that touches Layer-4 hooks, to confirm
  the regression suite (`tests/test_audit_hooks.cjs`) covers the
  new field.

## See also

- `.claude/hooks/post-tool-use.cjs` — the schema source of truth.
- `tests/test_audit_hooks.cjs` — regression suite for the hook
  emitters.
- `DIRECTIVES.md` `IMP-001` — append-only evidence rule.
