# Test Suite Overview

This directory contains regression tests for the Layer-3 slash
command and skill contracts plus the Layer-4 hooks.

## Overview

The hook protects the default branch by blocking certain git
operations. The hook suites validate eight bypass classes and
several baseline cases per the [hook README](../.claude/hooks/README.md).

The slash-command contract suite validates the shipped `/gov.*`
inventory, required YAML frontmatter, and prompt regressions that
must not drift back into the scaffold.

The skill contract suite validates the shipped `.claude/skills/`
inventory, reviewed skill-language regressions, and the
whitespace-tolerant frontmatter parsing enforced by
`scripts/check-governance.sh`.

**Test coverage:** hook regression suites plus Layer-3 contract
checks across Python (`unittest`) and JavaScript (`node:test`)

## Hook Test Specification (Single Source of Truth)

**File:** `hook_test_spec.yaml`

When the hook behavior changes, **update `hook_test_spec.yaml` first**, then ensure both test implementations reflect the specification:

```yaml
tests:
  - name: refspec_to_protected_blocks
    class: 2
    description: "Class 2: refspec-to-protected blocks regardless of HEAD"
    branch: feat/x
    command: "git push origin feat/x:main"
    expected_exit: 2
    check_stderr: "main"
```

## Test Files

### Slash commands: `test_command_contracts.py`

- Framework: `unittest`
- Coverage: `/gov.*` inventory, frontmatter keys, reviewed prompt
  regressions

Run with:

```bash
python3 tests/test_command_contracts.py
```

### Skills: `test_skill_contracts.py`

- Framework: `unittest`
- Coverage: skill inventory, frontmatter keys, reviewed prose
  regressions, and `check-governance.sh` skill-frontmatter behavior

Run with:

```bash
python3 tests/test_skill_contracts.py
```

### Python: `test_pre_tool_use_hook.py`

- Framework: `unittest`
- Coverage: 18 test cases
- Key functions:
  - `_git_env()` — git environment for subprocess calls
  - `_setup_repo()` — create temp repo on controlled branch
  - `_bash_payload()` — construct hook payload JSON
  - `_run_hook()` — invoke hook, capture output

Run with:

```bash
python3 -m unittest tests.test_pre_tool_use_hook -v
make hooks-test  # from root
```

### JavaScript: `test_pre_tool_use_hook.js`

- Framework: Node 20+ `node:test` (built-in)
- Coverage: 18 test cases
- Key functions: Same as Python, implemented in JavaScript

Run with:

```bash
node tests/test_pre_tool_use_hook.js
make hooks-test  # from root
```

## Adding a New Test Case

**Step 1:** Add to `hook_test_spec.yaml`:

```yaml
  - name: my_new_test
    class: 3
    description: "Class 3: [description]"
    branch: feat/x
    command: "git [command]"
    expected_exit: 2
    check_stderr: "keyword"
```

**Step 2:** Add test to `test_pre_tool_use_hook.py`:

```python
def test_my_new_test(self) -> None:
    """Class 3: [description]."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        _setup_repo(tmp_path, "feat/x")
        payload = _bash_payload("git [command]")
        result = _run_hook(payload, tmp_path)
    self.assertEqual(result.returncode, 2)
    self.assertIn("keyword", result.stderr.decode())
```

**Step 3:** Add test to `test_pre_tool_use_hook.js`:

```javascript
test("my new test", () => {
  const dir = setupRepo("feat/x");
  const result = runHook(bashPayload("git [command]"), dir);
  assert.equal(result.status, 2);
  assert.match(result.stderr, /keyword/);
});
```

**Step 4:** Run both test suites to verify:

```bash
make hooks-test
```

## Maintenance Notes

- **Both implementations must stay in sync** — when updating one, update the other
- **hook_test_spec.yaml is the reference** — it documents expected behavior
- **Test fixtures** (`tests/fixtures/*.json`) provide edge cases; update both if changed
- **Exit codes:** 0 = allowed, 2 = blocked (per hook protocol)

## Future Improvements

Template-based code generation could auto-generate both `.py` and `.js` test files from `hook_test_spec.yaml` via:

- Jinja2 template rendering in post-gen hook
- Or, standalone script in `scripts/` to regenerate tests

This would eliminate the 90% duplication and ensure perfect sync. See `/docs/OPTIMIZATION_ROADMAP.md` for details.

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
