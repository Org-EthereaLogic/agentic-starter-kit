# Test Suite Overview

This directory contains regression tests for the Layer-3 slash
command and skill contracts plus the Layer-4 hooks.

## Overview

The hook protects the default branch by blocking certain git
operations. The hook suites validate eight bypass classes and
several baseline cases per the [hook README](../.claude/hooks/README.md).

The slash-command contract suite validates the shipped
`.claude/commands/` inventory, required YAML frontmatter, and prompt
regressions that must not drift back into the scaffold.

The skill contract suite validates the shipped `.claude/skills/`
inventory, reviewed skill-language regressions, and the
whitespace-tolerant frontmatter parsing enforced by
`scripts/check-governance.sh`.

**Test coverage:** hook regression suites plus Layer-3 contract
checks across Python (`unittest`) and JavaScript (`node:test`).

## Hook Test Specification (Single Source of Truth)

**File:** `hook_test_spec.json`

`hook_test_spec.json` is consumed at import time by **both**
`test_pre_tool_use_hook.py` and `test_pre_tool_use_hook.js`. Each
scenario in the spec becomes one test in each language driver, so
adding, removing, or editing a case requires changes in exactly one
place — the JSON file. JSON was chosen over YAML so both languages
parse the spec with their standard library (no PyYAML / `js-yaml`
dependency).

### Spec schema

Top-level keys: `tests` (synthesized payloads) and `fixtures`
(payloads loaded from `tests/fixtures/<name>.json`). Each entry
supports the following fields:

| Field | Required | Notes |
| --- | --- | --- |
| `name` | yes | Unique identifier; becomes the Python `test_<name>` method. |
| `description` | yes | Human-readable; becomes the `node:test` test name. |
| `class` | yes | Bypass class (1–8 per `.claude/hooks/README.md`; `0` = baseline). |
| `branch` | optional | Initial repo branch. Omit / `null` to skip git setup. |
| `command` | one of | Bash command — wrapped as `{tool_name: "Bash", tool_input: {command}}`. |
| `tool_name` + `tool_input` | one of | Non-Bash payload — passed through verbatim. |
| `fixture` | one of | Filename under `tests/fixtures/`; payload loaded as-is. |
| `expected_exit` | yes | `0` = allow, `2` = block. |
| `check_stderr` | optional | Case-insensitive substring required in stderr; `null` skips. |

Cookiecutter renders `{{ cookiecutter.default_branch_name }}` inside
the JSON during template generation, so the rendered spec contains
the literal branch name (e.g. `"main"`).

### Adding a new test case

**Step 1** — Add an entry to `hook_test_spec.json`:

```json
{
  "name": "my_new_test",
  "class": 3,
  "description": "Class 3: [description]",
  "branch": "feat/x",
  "command": "git [command]",
  "expected_exit": 2,
  "check_stderr": "keyword"
}
```

**Step 2** — Run both suites. No driver edits required:

```sh
make hooks-test
```

## Test Files

### Slash commands: `test_command_contracts.py`

- Framework: `unittest`
- Coverage: command inventory, frontmatter keys, reviewed prompt
  regressions

Run with:

```sh
python3 tests/test_command_contracts.py
```

### Skills: `test_skill_contracts.py`

- Framework: `unittest`
- Coverage: skill inventory, frontmatter keys, reviewed prose
  regressions, `check-governance.sh` skill-frontmatter behavior, and
  the CRIT-002 regression that a corrupt `governance-rules.yaml` (a
  crashing governance loader) makes `check-governance.sh` exit
  non-zero with a diagnostic instead of vacuously passing

Run with:

```sh
python3 tests/test_skill_contracts.py
```

### Python hook driver: `test_pre_tool_use_hook.py`

- Framework: `unittest`
- Coverage: every entry under `tests` + `fixtures` in `hook_test_spec.json`
- Each scenario is attached to `PreToolUseHookTests` as `test_<name>` at
  import time, so individual selectors still work:

```sh
python3 -m unittest tests.test_pre_tool_use_hook -v
python3 -m unittest tests.test_pre_tool_use_hook.PreToolUseHookTests.test_refspec_to_protected_blocks
make hooks-test  # from repo root
```

### JavaScript hook driver: `test_pre_tool_use_hook.js`

- Framework: Node 20+ `node:test` (built-in)
- Coverage: same scenarios via the same JSON spec
- Each scenario becomes one `test(description, …)` call.

Run with:

```sh
node --test tests/test_pre_tool_use_hook.js
node --test tests/test_pre_tool_use_hook.js --grep "refspec to protected blocks"
make hooks-test  # from repo root
```

## Maintenance Notes

- **Spec is canonical** — `hook_test_spec.json` is the only place to
  add or modify hook regression cases. Drivers iterate it.
- **Fixtures stay in `tests/fixtures/`** — `*.json` payload files are
  referenced by `fixture: "<filename>"` entries in the spec.
- **Exit codes:** `0` = allowed, `2` = blocked (per hook protocol).
- **Both languages must run green** — `make hooks-test` invokes the
  driver(s) appropriate for the rendered project's `primary_language`.

## Common Issues

### "Tests pass on my machine but fail in CI"

- Ensure Node.js is v20+: `node --version`
- Ensure Python 3.11+: `python3 --version`
- Check git is configured: `git config user.email` (should not be empty)

### "How do I test a single case?"

- Python: `python3 -m unittest tests.test_pre_tool_use_hook.PreToolUseHookTests.test_refspec_to_protected_blocks`
- JavaScript: `node --test tests/test_pre_tool_use_hook.js --grep "refspec to protected blocks"`

## References

- [Hook design](../.claude/hooks/README.md) — bypass classes 1-8
- [CRIT-008 directive](../DIRECTIVES.md) — hook regression suite requirement
- Test fixtures (`.json` payloads under `tests/fixtures/`)
