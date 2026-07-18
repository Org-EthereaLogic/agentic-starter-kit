# Git-layer hooks — {{ cookiecutter.project_name }}

This directory holds the **primary, enforced** CRIT-008 boundary: the
git hooks that block direct commits on and pushes to a protected branch
(the render-time default branch `{{ cookiecutter.default_branch_name }}`
plus the legacy `master`).

They run **after** the shell has expanded, aliased, and word-split the
command — git invokes them no matter how `git commit`/`git push` was
spelled — so they cannot be dodged by the shell idioms that defeat a
command-string matcher (`eval`, `exec`, `\git`, `git${IFS}push`,
`bash -cl`, `sudo`/`doas`, `stdbuf`/`setsid`, `&` chains). The Claude
Code hook `../.claude/hooks/pre-tool-use.js` remains as fast,
agent-facing **defense-in-depth**, not the guarantee.

---

## What lives here

| File | Trigger | Enforces |
|---|---|---|
| `pre-commit` | `git commit`, `git commit --amend` | Blocks the commit when the current branch (`git symbolic-ref --short HEAD`, falling back to `git rev-parse --abbrev-ref HEAD`) is protected. Fails **closed** if the branch cannot be resolved. |
| `pre-merge-commit` | merge commits — a non-fast-forward, conflict-free `git merge` that records a merge commit automatically | Blocks the merge when the current (destination) branch is protected, with the **same** resolution + fail-closed logic as `pre-commit`. A **conflicted** merge stops and is finished with a later `git commit`, which `pre-commit` then catches. |
| `pre-push` | `git push` (all forms) | Reads the pre-push stdin refspec lines (`<local ref> <local sha> <remote ref> <remote sha>`) and blocks when **any** pushed remote ref resolves to a protected branch — covering `git push origin HEAD`, `git push origin feat/x:{{ cookiecutter.default_branch_name }}`, `git push --all`/`--mirror` (one stdin line per ref), implicit-upstream pushes, and **deletes** of a protected ref. Matches by exact string equality on the `refs/heads/`-stripped destination path only (never substring, never basename), so `feat/x:mainline` does **not** match `{{ cookiecutter.default_branch_name }}`, and a legitimately named feature branch such as `release/{{ cookiecutter.default_branch_name }}` or `dependabot/master` is **not** over-blocked. |

All three hooks are POSIX `sh` with no Node/Python dependency, so they
are never pruned for any `primary_language` and run on the leanest
checkout.

### Which git operations invoke a commit-time hook — the honest map

Git does **not** run a client-side commit-time hook for every way a
commit can land on the current branch. This matters because the current
branch may be a protected one:

| Operation | Commit-time hook git runs | Blocked at the git layer? |
|---|---|---|
| `git commit`, `git commit --amend` | `pre-commit` | **Yes** |
| `git merge --no-ff` (conflict-free merge commit) | `pre-merge-commit` | **Yes** |
| `git merge` that **conflicts** | none, then `pre-commit` on the finishing `git commit` | **Yes** (via `pre-commit`) |
| `git cherry-pick`, `git revert`, `git rebase`, `git am` replaying commits **conflict-free** | **none** | **No** (documented limitation — see below) |

`cherry-pick`/`revert`/`rebase`/`am` replay commits directly onto the
current branch **without invoking any commit-time hook** when they apply
cleanly, so the git layer does **not** stop those commits from landing on
a **local** protected branch. This is a git behavior, not a gap we can
close with another `.githooks` script. The backstops that **do** hold:

1. **`pre-push`** blocks pushing *any* resulting commit to the protected
   **remote** — so a locally-replayed commit cannot reach the shared
   branch through this clone.
2. **Agent-layer `../.claude/hooks/pre-tool-use.js`** early-blocks the
   porcelain/`eval`/`\git` spellings of `cherry-pick`/`revert`/`rebase`/
   `merge` that an autonomous agent would issue, before the git
   subprocess starts.
3. **Server-side branch protection** on the forge is the true backstop
   (see the honest-boundary section below).

This sits beside the `--no-verify` / unset-`core.hooksPath` boundary list
below: all of it is documented rather than overclaimed.

## Install

```sh
make hooks-install          # git config core.hooksPath .githooks
```

`core.hooksPath` makes git use `.githooks/` and **ignore** `.git/hooks/`.
The install is idempotent (running it twice re-writes the same key) and
is a prerequisite of `make hooks-test` (hence of `make validate`). It is
also wired into `.devcontainer/post-create.sh` and surfaced in the
cookiecutter post-generation "Next steps", so freshly-scaffolded and
dev-container checkouts get the boundary by default.

## Interaction with the pre-commit framework

`.pre-commit-config.yaml` ships in this template, and `CONTRIBUTING.md`
tells contributors to run `pre-commit install`, which writes shims into
`.git/hooks/`. Once `core.hooksPath` points at `.githooks/`, git
**ignores** `.git/hooks/` — so those framework shims would silently stop
running. This is the one real conflict, and it is resolved by
**chaining** rather than by choosing one over the other:

- After the branch guard passes, `pre-commit`, `pre-merge-commit`, and
  `pre-push` invoke `pre-commit hook-impl --config=.pre-commit-config.yaml
  --hook-type=<stage> --skip-on-missing-config -- "$@"` **when** a
  `pre-commit` binary **and** `.pre-commit-config.yaml` are both present.
  `hook-impl` is exactly the entrypoint the framework's own installed
  shim calls, so nothing the framework configured (ruff, ruff-format,
  the local `governance-check` / `marker-scan` / `check-traceability` /
  `check-doc-drift` hooks, …) is lost. `pre-push` re-feeds the stdin it
  captured for its own check to the chained invocation.
- When `pre-commit` is not installed (a fresh clone, or the temp repo in
  `tests/test_git_hooks.sh`), chaining is a clean **no-op** — identical
  to today's behavior where the framework simply is not active. A
  legitimate commit's PASS path never depends on the framework being
  installed.

Net effect: `pre-commit install` becomes unnecessary once
`core.hooksPath` is wired (the chain reproduces it), but leaving it
installed is harmless — git ignores `.git/hooks/` under `core.hooksPath`
and the chain runs the same hooks.

## Honest boundary — what this does and does not defend

These hooks are an **operator-integrity control, not a sandbox.** They
guarantee that, on a checkout wired with `make hooks-install`, the
protected branches cannot be committed to or pushed to by *any* shell
spelling of a git command. They do **not** defend against:

- a user who deliberately unsets or overrides `core.hooksPath`
  (`git -c core.hooksPath= …`, `git config --unset core.hooksPath`),
- a maliciously mutated `.git/hooks` or `.githooks`,
- `git commit --no-verify` / `git push --no-verify` (which bypasses
  client-side hooks by design),
- server-side history rewrites outside this clone.

For those, the real control is a **server-side / branch-protection**
policy on the forge (e.g. GitHub protected-branch rules and required
reviews). This directory raises the floor for honest local workflows and
autonomous agents; it does not claim to be a security sandbox. See
`../DIRECTIVES.md` CRIT-008 and `../docs/THREAT_MODEL.md`.

## How to test

```sh
make hooks-test             # runs tests/test_git_hooks.sh (+ the agent-layer suites)
sh tests/test_git_hooks.sh  # git-layer suite directly
```

`tests/test_git_hooks.sh` installs these hooks in a throwaway temp repo
(local `core.hooksPath`, robust against `GIT_CONFIG_GLOBAL=/dev/null`),
creates a local bare remote, and asserts every shell idiom is blocked on
a protected target while feature-branch commits/pushes still succeed. It
also asserts that a `git merge --no-ff` into a protected branch (and its
`eval`/`\git` spellings) is blocked by `pre-merge-commit`, that a
feature-branch merge still succeeds, and — for the documented limitation
— that a `cherry-pick`/`revert` onto a protected branch **lands locally**
(recorded as the known git behavior, not a failure) but the subsequent
`git push origin {{ cookiecutter.default_branch_name }}` of that state is
**blocked by `pre-push`**, proving the backstop holds. Idioms whose
wrapper binary is absent or cannot run non-interactively (`setsid`,
`sudo`, `doas` — notably on macOS) are **skipped with a printed reason**,
never assumed to pass.

## See also

- `../.claude/hooks/README.md` — the agent-layer defense-in-depth hook.
- `../DIRECTIVES.md` `CRIT-008` — the directive this boundary enforces.
- `../governance-rules.yaml` — CRIT-008 rule + enforcement map.
- `../CONTRIBUTING.md` — contributor setup (`pre-commit install`,
  superseded-but-harmless under `core.hooksPath`).
