---
description: Quick repo health check — branch, diff stats, open PRs, marker-scan
allowed-tools: Bash
---

# status

Lightweight repo health check for mid-session check-ins. Does not
run the full validation suite — use `/test` or `/audit` for
that.

## Context snapshot

- Branch: !`git branch --show-current`
- Status: !`git status --short`
- Ahead/behind {{ cookiecutter.default_branch_name }}: !`git rev-list --left-right --count origin/{{ cookiecutter.default_branch_name }}...HEAD 2>/dev/null || echo "upstream not configured"`
- Recent commits: !`git log --oneline -5`
- Open PRs by you: !`gh pr list --author @me --state open 2>/dev/null || echo "gh not authenticated"`

## Run

1. `make marker-scan` — quick governance pulse (`CRIT-001`).
2. Summarize the snapshot data above.

## Report

Return a concise markdown block:

```text
=== Status ===
Branch: <name>
Working tree: clean | N modified, M untracked
Ahead/behind {{ cookiecutter.default_branch_name }}: <+N / -N>
Marker-scan: pass | <N hits in paths>
Open PRs: <count>
Recent commits: <last 3 subjects>
```

No prose commentary beyond the block.
