# `.claude/agents/` — specialized subagents

Curated subagent definitions for Claude Code in
{{ cookiecutter.project_name }}. Each agent has narrow scope, a
curated tool allowlist, and YAML frontmatter declaring `name`,
`description`, `model`, and `memory`. The full per-agent
contracts live in the individual `.md` files.

## Inventory

| Agent | Role | When to use |
| --- | --- | --- |
| `lead-software-engineer` | Implementation | Translating accepted specs into source, tests, and evidence. |
| `sdlc-technical-writer` | Documentation | Authoring or revising specs, security requirements, ADR/RFC, READMEs. |
| `test-automator` | Test strategy | Authoring tests, hook regression suites, evidence-quality enforcement. |
| `ux-delight-specialist` | Operator surface | CLI output, dashboard, error ergonomics, empty/loading states. |
| `python-pro` *(Python or polyglot path only)* | Typed Python | `pyproject.toml`, `uv`, ruff, `{{ cookiecutter.python_typechecker }}`. |
| `typescript-pro` *(TypeScript or polyglot path only)* | Typed TypeScript | `package.json`, `tsconfig.json`, ESLint, vitest. |
| `security-reviewer` | Security verification | Threat-model, SBOM triage, secrets policy, attack-surface review. |
| `governance-auditor` | Scaffold audit | Read-only audit of the five-layer governance stack; drives `governance-review` CLI. |

The conditional language agent (`python-pro` or `typescript-pro`)
is selected by `hooks/post_gen_project.py` based on
`primary_language`. The polyglot path keeps both.

## Coverage check

`scripts/check-governance.sh` verifies the inventory above is
present after rendering. The audit role itself
(`governance-auditor`) replays the same check from inside an
agent session.
