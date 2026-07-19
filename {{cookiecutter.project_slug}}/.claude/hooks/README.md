# Claude Code hooks — {{ cookiecutter.project_name }}

This directory holds the Layer 4 runtime-enforcement hooks that
execute inside Claude Code on tool-use events. The hook in this
directory is registered in `.claude/settings.json`.

> **CRIT-008 boundary — read this first.** `pre-tool-use.js` is
> **best-effort defense-in-depth**, not the CRIT-008 guarantee. It
> inspects the proposed command *string* before the shell resolves it,
> so shell idioms (`eval`, `exec`, `\git`, `git${IFS}push`, `bash -cl`,
> `sudo`/`doas`, `stdbuf`/`setsid`, `&` chains) can defeat it
> ([issue #102](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/102)).
> The **primary, enforced** boundary is the git-layer hook —
> [`../../.githooks/`](../../.githooks/README.md) (`pre-commit` +
> `pre-merge-commit` + `pre-push`, installed via
> `git config core.hooksPath .githooks` / `make hooks-install`) —
> which runs *after* shell resolution and
> therefore cannot be dodged by shell syntax. This hook's value is
> **speed**: it blocks the obvious cases early, in the agent's own
> turn, before a `git` subprocess even starts.

---

## What lives here

| File | Trigger | Purpose |
|---|---|---|
| `pre-tool-use.js` | `PreToolUse:Bash` | Fast agent-facing early block of Bash commands that would commit on or push to a protected branch. Defense-in-depth for `CRIT-008`; the enforced boundary is `../../.githooks/`. |

The protected-branch list is configured at template-render time:
the user-chosen `default_branch_name` cookiecutter variable, plus
the literal `master` as a legacy guard. The git-layer hooks in
`../../.githooks/` use the same protected set.

## Why a hard block

The hook's exit-2 contract returns the block reason on stderr and
the Claude Code harness surfaces that reason to the model, which
adjusts approach (typically by branching from the protected
branch). A prompt-style permission gate would not stop an
autonomous subagent running with permission prompts disabled — so
this early block is worthwhile even though it is not the boundary of
record. `CONSTITUTION.md §P3` declares the directive a hard policy
boundary; the git-layer hooks in `../../.githooks/` are its enforced
mechanism, and this hook is the fast agent-facing complement.

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

Classes 9–15 close the seven bypass classes documented in
[issue #102](https://github.com/Org-EthereaLogic/agentic-starter-kit/issues/102)
(CRIT-008 hardening):

9. **`HEAD` refspec destination.** `git push origin HEAD` while HEAD
   is on a protected branch — the `HEAD`/`@` destination is
   normalized to the current branch before the protected-set check.
10. **Single `&` separator.** `true & git push origin main` — a
    single `&` job-control separator splits into subcommands like
    `&&` (not only the double form).
11. **Combined short-flag nested shells.** `bash -lc "git push
    origin main"` — flag clusters ending in `c` (`-lc`, `-ic`) are
    recognized as `-c` invocations.
12. **Quoted nested-shell payloads.** `bash -c 'git push origin
    main; true'` — the quote-aware splitter keeps the quoted payload
    intact so the inner `;`/`|` is only re-split once the payload is
    extracted and recursively evaluated.
13. **Trivial command wrappers.** `env`, `command`, `nice`, `xargs`,
    `nohup`, `time`, `timeout` prefixes around git (`env git push
    origin main`) are peeled — with their own flags and the value
    `nice -n`/`timeout` take — before the git check.
14. **`--branches` broad push.** `git push --branches origin` is
    blocked as a broad push mode, the git ≥ 2.44 synonym of `--all`.
15. **Fail-closed on branch-lookup failure.** For an
    otherwise-matching `git push`/`git commit`/commit-producing
    command, a failed current-branch lookup blocks (exit 2) rather
    than allowing. Scoped to already-matched git commands: a plain
    non-git command in a non-git directory still passes through.

Classes 16–17 close two residual bypasses of the same classes caught
at the test gate during issue #102 hardening:

16. **`c`-not-last nested-shell clusters.** `bash -cl "git push
    origin main"`, `sh -ci "..."`, `bash -cx "..."` — the earlier
    fix only recognized clusters *ending* in `c` (`-lc`, `-ic`). Any
    single-dash short-flag cluster that contains `c` in any position
    is now treated as a `-c` invocation, while `--command` long forms
    and non-`c` clusters (`-l`, `-il`, `--login`) are unchanged.
17. **`sudo` wrapper.** `sudo git push origin main`, `sudo -u <user>
    git push …`, `sudo -n git …` — `sudo` is peeled as a trivial
    wrapper (with its arg-taking options `-u`/`-g`/`-p`/… consumed)
    before the git check. Non-git targets such as `sudo systemctl
    restart nginx` still pass through.

Classes 18–19 close two wrapper idioms found at the merge-family test
gate (agent-layer defense-in-depth for the git-layer `pre-merge-commit`
boundary):

18. **`eval` wrapper.** `eval 'git cherry-pick …'`, `eval "git merge
    …"` — `eval` hides a real git command inside a quoted argument. The
    quoted payload is extracted and recursively evaluated, so a
    commit-producing subcommand on a protected branch is caught, while
    read-only (`eval 'git status'`) and non-git (`eval 'npm run build'`)
    payloads pass through.
19. **Backslash-escaped command token.** `\git merge …`, `\git commit
    …` — a single leading backslash suppresses alias/function
    resolution but runs the same binary. It is stripped from the
    resolved command token before the git check, so `\git` merge/commit
    on a protected branch is caught, while `\git status` off a protected
    branch stays allowed.

> These two are **agent-layer defense-in-depth only.** The enforced
> merge boundary is the git-layer `../../.githooks/pre-merge-commit`
> hook, which git invokes for a non-fast-forward conflict-free merge
> regardless of how it was spelled. Note that git runs **no** commit-time
> hook for a conflict-free `cherry-pick`/`revert`/`rebase`/`am`, so a
> locally-replayed commit on a protected branch is stopped only by
> `pre-push` (on push), this agent-layer hook (for the agent's porcelain/
> `eval`/`\git` forms), and server-side branch protection — see
> `../../.githooks/README.md`.

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

The `make hooks-test` target wraps both, and now also runs the
git-layer boundary suite `tests/test_git_hooks.sh` unconditionally
(POSIX sh, language-neutral) — it installs the `.githooks` in a temp
repo and asserts every shell idiom that defeats *this* string-layer
hook is blocked at the git layer. The suite runs as part of
`make validate`.

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

- `../../.githooks/README.md` — the git-layer hooks that are the
  **primary enforced** CRIT-008 boundary (this hook is defense-in-depth).
- `DIRECTIVES.md` `CRIT-008` — the directive both layers enforce.
- `CONSTITUTION.md §P3` — Hard Policy Boundaries.
- `../settings.json` — hook registration on `PreToolUse:Bash`.
- `../../tests/test_pre_tool_use_hook.py` /
  `../../tests/test_pre_tool_use_hook.js` — regression suite.
- `../../tests/fixtures/` — sample payloads.
