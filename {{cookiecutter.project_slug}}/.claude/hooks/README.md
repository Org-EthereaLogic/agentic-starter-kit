# Claude Code hooks — {{ cookiecutter.project_name }}

This directory holds the Layer 4 runtime-enforcement hooks that
execute inside Claude Code on tool-use events. The hook in this
directory is registered in `.claude/settings.json`.

---

## What lives here

| File | Trigger | Purpose |
|---|---|---|
| `pre-tool-use.js` | `PreToolUse:Bash` | Blocks Bash commands that would commit on or push to a protected branch. Implements `CRIT-008`. |

The protected-branch list is configured at template-render time:
the user-chosen `default_branch_name` cookiecutter variable, plus
the literal `master` as a legacy guard.

## Why a hard block

The hook's exit-2 contract returns the block reason on stderr and
the Claude Code harness surfaces that reason to the model, which
adjusts approach (typically by branching from the protected
branch). A prompt-style permission gate would not stop an
autonomous subagent running with permission prompts disabled — the
hook is the only reliable choke point. `CONSTITUTION.md §P3`
declares the directive a hard policy boundary; this file is its
enforcement.

## Bypass classes covered

The hook covers the bypass classes a coding agent has actually
attempted under load:

1. **Direct push to a protected branch.** `git push origin main`
   from any HEAD.
2. **Refspec push targeting a protected branch.** `git push origin
   feat/x:main` from a non-protected HEAD.
3. **Implicit push from a protected HEAD.** `git push` with no
   refspec while HEAD is on a protected branch.
4. **Broad push modes.** `git push --all` and `git push --mirror`
   regardless of HEAD.
5. **Direct commit on a protected branch.** `git commit ...` while
   HEAD is on a protected branch.
6. **Commit-producing subcommands on a protected branch.** `git
   merge`, `git rebase`, `git cherry-pick`, `git revert`, `git am`,
   `git pull` while HEAD is on a protected branch.
7. **Nested-shell escapes.** `bash -c "git push origin main"`
   (and the `sh`, `zsh`, `--command=` variants) — re-evaluated
   against the inline payload.
8. **Chained subcommands.** `&&`, `||`, `;`, `|`, and newline
   separators — each subcommand is evaluated independently.

## How to test the hook

The regression suite is at `tests/test_pre_tool_use_hook.py`
(Python path) and `tests/test_pre_tool_use_hook.js` (TypeScript
path). Polyglot projects keep both.

```sh
# Python path
python -m unittest tests/test_pre_tool_use_hook.py -v

# TypeScript path
node --test tests/test_pre_tool_use_hook.js
```

The `make hooks-test` target wraps both. Once the build glue is
scaffolded (Phase 4 of the upstream template build), the suite
runs as part of `make validate`.

## Ad-hoc invocation

The hook reads a JSON payload from stdin per the Claude Code hook
protocol:

```sh
node .claude/hooks/pre-tool-use.js < tests/fixtures/protected-push.json
echo $?  # expect 2; stderr contains the block reason
```

The `tests/fixtures/` directory ships sample payloads for every
bypass class so the hook can be exercised by hand without running
the full test suite.

## Discovery protocol — new bypass classes

When a new bypass class is discovered (an agent finds a way to
commit on or push to a protected branch that the current hook
allows), follow this order strictly:

1. **Add a regression test first.** `tests/test_pre_tool_use_hook.{py,js}`
   gets a new test case that asserts the bypass currently *fails*
   to be blocked. Commit this on a `fix/<slug>` branch. The test
   is initially expected to *fail*.
2. **Patch the hook.** Update `pre-tool-use.js` to detect the new
   bypass pattern. Re-run the suite — the new test now passes,
   and the existing tests remain green.
3. **Document in the changelog (Phase-12 onward).** Once the
   `CHANGELOG.md` lands per `GAP-EXT-010`, every new bypass class
   gets an entry under `Security` documenting what was caught and
   when.

The order matters. Patching first and adding the test
second risks the test silently drifting to allow the pattern it
was meant to catch.

## Disabling the hook (emergency only)

To temporarily disable the hook (for example, when the protected-
branch policy needs to be bypassed for a documented incident):

1. Edit `.claude/settings.json` to remove or comment out the
   `PreToolUse:Bash` registration. JSON does not support comments;
   removing the registration entirely is the only valid form.
2. Document the deviation in a sync record under `report/` per
   `IMP-001`. Reference the incident, the deviation window, and
   the remediation.
3. Re-enable the hook before the next merge to the default
   branch.

The hook is registered, exercised by tests, and verified by
`make governance-check` (Phase 4 onward) — disabling it without
re-enabling will fail every subsequent gate.

## See also

- `DIRECTIVES.md` `CRIT-008` — the directive this hook enforces.
- `CONSTITUTION.md §P3` — Hard Policy Boundaries.
- `../settings.json` — hook registration on `PreToolUse:Bash`.
- `../../tests/test_pre_tool_use_hook.py` /
  `../../tests/test_pre_tool_use_hook.js` — regression suite.
- `../../tests/fixtures/` — sample payloads.
