#!/bin/sh
# tests/test_git_hooks.sh — regression suite for the git-layer CRIT-008
# protected-branch hooks (.githooks/pre-commit, .githooks/pre-push).
#
# WHY this test exists: the Claude Code PreToolUse:Bash hook
# (.claude/hooks/pre-tool-use.js) inspects the proposed command STRING
# before the shell resolves it, so shell idioms (eval, exec, \git,
# git${IFS}push, bash -cl, sudo, stdbuf/setsid, & chains) can defeat it.
# The git-layer hooks run AFTER shell resolution — git invokes them no
# matter how `git commit`/`git push` was spelled — so they cannot be
# dodged by shell syntax. This suite proves that by running every such
# idiom as a REAL shell command against a temp repo with the hooks
# installed, asserting each protected-branch operation is actually
# rejected (non-zero AND no side effect), while feature-branch
# operations still succeed.
#
# Coverage: commit idioms (pre-commit), push idioms (pre-push), and
# non-fast-forward conflict-free MERGE idioms (pre-merge-commit). It also
# records the documented git limitation — a conflict-free cherry-pick/
# revert runs NO commit-time hook, so it CAN land a commit on a LOCAL
# protected branch — and asserts the pre-push backstop blocks pushing
# that state to the protected remote.
#
# Language-neutral POSIX sh: never pruned by hooks/post_gen_project.py
# (which only prunes the py/js hook-test twins), so it runs for every
# primary_language. Invoked unconditionally by `make hooks-test`.
#
# This file IS Jinja-rendered (tests/*.sh is not in cookiecutter.json
# _copy_without_render), so the protected default below renders to the
# chosen branch name. Verification is always done against a render; the
# un-rendered literal is an invalid git branch name (contract constraint).

# Deliberately NOT `set -e`: we run commands expected to fail and inspect
# their exit codes.
set -u

PROTECTED="{{ cookiecutter.default_branch_name }}"

# Prove the install is robust against the harness's git-config isolation.
GIT_CONFIG_GLOBAL=/dev/null
GIT_CONFIG_SYSTEM=/dev/null
export GIT_CONFIG_GLOBAL GIT_CONFIG_SYSTEM

# Locate the checked-in hooks dir from this script's own location, so
# the suite works from any cwd (make runs it from the project root).
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
GITHOOKS="$REPO_ROOT/.githooks"

PASS=0
FAIL=0
SKIP=0
TMPDIRS=""

cleanup() {
	for d in $TMPDIRS; do
		[ -n "$d" ] && rm -rf "$d"
	done
}
trap cleanup EXIT INT TERM

pass() { printf 'PASS: %s\n' "$1"; PASS=$((PASS + 1)); }
fail() { printf 'FAIL: %s\n' "$1"; FAIL=$((FAIL + 1)); }
skip() { printf 'SKIP: %s (%s)\n' "$1" "$2"; SKIP=$((SKIP + 1)); }

# Create a fresh temp repo with the git-layer hooks installed LOCALLY,
# seed a commit on a feature branch (so setup is never blocked), add a
# feat/x branch (a valid, non-protected refspec source), and a local
# bare remote for real push tests. Leaves cwd inside the work tree.
fresh_repo() {
	_tmp="$(mktemp -d 2>/dev/null)" || { echo "mktemp failed"; exit 1; }
	TMPDIRS="$TMPDIRS $_tmp"
	git init -q -b feat/seed "$_tmp/work" 2>/dev/null || {
		# Older git without `init -b`: init then rename the unborn branch.
		git init -q "$_tmp/work"
		git -C "$_tmp/work" symbolic-ref HEAD refs/heads/feat/seed
	}
	git -C "$_tmp/work" config user.email "test@example.com"
	git -C "$_tmp/work" config user.name "Hook Test"
	git -C "$_tmp/work" commit -q --allow-empty -m seed
	git -C "$_tmp/work" branch feat/x
	# Install the git-layer hooks LOCALLY. Local .git/config is unaffected
	# by GIT_CONFIG_GLOBAL/SYSTEM=/dev/null, so the hooks fire even under
	# the harness isolation above.
	git -C "$_tmp/work" config core.hooksPath "$GITHOOKS"
	git init -q --bare "$_tmp/remote.git"
	git -C "$_tmp/work" remote add origin "$_tmp/remote.git"
	cd "$_tmp/work" || exit 1
}

on_protected() { git checkout -q -B "$PROTECTED"; }

# Assert a commit attempt was blocked by the hook: it must exit non-zero
# AND leave HEAD unchanged (proving the block came from the hook, not an
# incidental failure that also happened to make no commit).
check_commit_blocked() {
	_label="$1"; _rc="$2"; _before="$3"
	_after="$(git rev-parse HEAD 2>/dev/null || echo none)"
	if [ "$_rc" -ne 0 ] && [ "$_before" = "$_after" ]; then
		pass "$_label"
	else
		fail "$_label [rc=$_rc before=$_before after=$_after]"
	fi
}

# Assert a push attempt was blocked: non-zero exit AND the protected ref
# is absent from the bare remote (proving nothing landed).
check_push_blocked() {
	_label="$1"; _rc="$2"
	if [ "$_rc" -ne 0 ] && ! git ls-remote --heads origin "$PROTECTED" 2>/dev/null | grep -q .; then
		pass "$_label"
	else
		fail "$_label [rc=$_rc; protected ref present in remote?]"
	fi
}

printf '=== git-layer protected-branch hook suite (protected: %s, master) ===\n' "$PROTECTED"
printf 'hooks dir: %s\n\n' "$GITHOOKS"

# Sanity: the hooks must exist and be executable, or every case is moot.
if [ ! -x "$GITHOOKS/pre-commit" ] || [ ! -x "$GITHOOKS/pre-merge-commit" ] || [ ! -x "$GITHOOKS/pre-push" ]; then
	echo "FATAL: $GITHOOKS/pre-commit, pre-merge-commit, and pre-push must exist and be executable"
	exit 1
fi

# ---------------------------------------------------------------------
# COMMIT idioms — each must be blocked on the protected branch.
# ---------------------------------------------------------------------

# C1: eval
fresh_repo; on_protected
b="$(git rev-parse HEAD)"
eval 'git commit --allow-empty -m blocked' >/dev/null 2>&1; rc=$?
check_commit_blocked "eval 'git commit' on protected" "$rc" "$b"

# C2: exec (wrapped in sh -c so the exec replaces the child, not us)
fresh_repo; on_protected
b="$(git rev-parse HEAD)"
sh -c 'exec git commit --allow-empty -m blocked' >/dev/null 2>&1; rc=$?
check_commit_blocked "sh -c 'exec git commit' on protected" "$rc" "$b"

# C3: backslash-git (alias-bypass idiom)
fresh_repo; on_protected
b="$(git rev-parse HEAD)"
\git commit --allow-empty -m blocked >/dev/null 2>&1; rc=$?
check_commit_blocked "\\git commit on protected" "$rc" "$b"

# C4: bash -cl (login+command shell, combined short-flag cluster)
if command -v bash >/dev/null 2>&1; then
	fresh_repo; on_protected
	b="$(git rev-parse HEAD)"
	bash -cl 'git commit --allow-empty -m blocked' >/dev/null 2>&1; rc=$?
	check_commit_blocked "bash -cl \"git commit\" on protected" "$rc" "$b"
else
	skip "bash -cl \"git commit\" on protected" "bash not installed"
fi

# C5: stdbuf (line-buffering wrapper; absent on stock macOS)
if command -v stdbuf >/dev/null 2>&1; then
	fresh_repo; on_protected
	b="$(git rev-parse HEAD)"
	stdbuf -oL git commit --allow-empty -m blocked >/dev/null 2>&1; rc=$?
	check_commit_blocked "stdbuf -oL git commit on protected" "$rc" "$b"
else
	skip "stdbuf -oL git commit on protected" "stdbuf not installed (expected on macOS)"
fi

# C6: setsid (new-session wrapper; absent on stock macOS). Require `-w`
# so setsid WAITS and propagates git's exit status — without it some
# util-linux builds fork and return 0 immediately, which would mask the
# hook's non-zero block. Skip (never assume-pass) when setsid or its -w
# flag is unavailable.
if command -v setsid >/dev/null 2>&1 && setsid -w true >/dev/null 2>&1; then
	fresh_repo; on_protected
	b="$(git rev-parse HEAD)"
	setsid -w git commit --allow-empty -m blocked >/dev/null 2>&1; rc=$?
	check_commit_blocked "setsid -w git commit on protected" "$rc" "$b"
elif command -v setsid >/dev/null 2>&1; then
	skip "setsid -w git commit on protected" "setsid present but lacks -w (cannot capture exit status reliably)"
else
	skip "setsid -w git commit on protected" "setsid not installed (expected on macOS)"
fi

# C7: sudo -n. Only run if sudo can reach git non-interactively AND
# operate on this repo (no dubious-ownership refusal); otherwise a
# non-zero exit would be unattributable to the hook — SKIP, never assume.
if command -v sudo >/dev/null 2>&1; then
	fresh_repo; on_protected
	if sudo -n git rev-parse --git-dir >/dev/null 2>&1; then
		b="$(git rev-parse HEAD)"
		sudo -n git commit --allow-empty -m blocked >/dev/null 2>&1; rc=$?
		check_commit_blocked "sudo -n git commit on protected" "$rc" "$b"
	else
		skip "sudo -n git commit on protected" "sudo cannot run git non-interactively on this repo"
	fi
else
	skip "sudo -n git commit on protected" "sudo not installed"
fi

# C8: doas (BSD privilege wrapper; rare on Linux/macOS CI).
if command -v doas >/dev/null 2>&1; then
	fresh_repo; on_protected
	if doas -n git rev-parse --git-dir >/dev/null 2>&1; then
		b="$(git rev-parse HEAD)"
		doas -n git commit --allow-empty -m blocked >/dev/null 2>&1; rc=$?
		check_commit_blocked "doas git commit on protected" "$rc" "$b"
	else
		skip "doas git commit on protected" "doas cannot run git non-interactively on this repo"
	fi
else
	skip "doas git commit on protected" "doas not installed"
fi

# ---------------------------------------------------------------------
# PUSH idioms — each must be blocked; nothing lands in the bare remote.
# ---------------------------------------------------------------------

# P1: plain push of HEAD while on protected
fresh_repo; on_protected
git push -q origin HEAD >/dev/null 2>&1; rc=$?
check_push_blocked "git push origin HEAD on protected" "$rc"

# P2: eval push
fresh_repo; on_protected
eval 'git push -q origin HEAD' >/dev/null 2>&1; rc=$?
check_push_blocked "eval 'git push origin HEAD' on protected" "$rc"

# P3: git\${IFS}push (word-split via IFS defeats a literal-string matcher)
fresh_repo; on_protected
git${IFS}push -q origin HEAD >/dev/null 2>&1; rc=$?
check_push_blocked "git\${IFS}push origin HEAD on protected" "$rc"

# P4: background & job-control separator before the real push
fresh_repo; on_protected
true & git push -q origin HEAD >/dev/null 2>&1; rc=$?
wait 2>/dev/null
check_push_blocked "true & git push origin HEAD on protected" "$rc"

# P5: refspec that targets the protected branch from a feature source
fresh_repo
git checkout -q feat/seed
git push -q origin "feat/x:$PROTECTED" >/dev/null 2>&1; rc=$?
check_push_blocked "git push origin feat/x:$PROTECTED (refspec)" "$rc"

# ---------------------------------------------------------------------
# MERGE idioms — a non-fast-forward, conflict-free merge that records a
# merge commit on a protected branch is blocked by pre-merge-commit. git
# invokes that hook itself, so the eval/\git spellings are irrelevant to
# the git layer (they still run real `git merge`), but we exercise them
# anyway to prove the boundary holds for every spelling.
# ---------------------------------------------------------------------

# Leave cwd on PROTECTED (at feat/seed) with feat/x one commit AHEAD, so
# `git merge --no-ff feat/x` must record a merge commit (invoking
# pre-merge-commit) rather than fast-forwarding silently.
setup_merge_into_protected() {
	fresh_repo
	git checkout -q feat/x
	git commit -q --allow-empty -m "feat work ahead of seed"
	git checkout -q -B "$PROTECTED" feat/seed
}

# M1: plain non-ff merge into protected
setup_merge_into_protected
b="$(git rev-parse HEAD)"
git merge --no-ff -m "merge feat/x" feat/x >/dev/null 2>&1; rc=$?
check_commit_blocked "git merge --no-ff feat/x into protected" "$rc" "$b"

# M2: eval-wrapped merge into protected
setup_merge_into_protected
b="$(git rev-parse HEAD)"
eval 'git merge --no-ff -m "merge feat/x" feat/x' >/dev/null 2>&1; rc=$?
check_commit_blocked "eval 'git merge --no-ff feat/x' into protected" "$rc" "$b"

# M3: backslash-git merge into protected
setup_merge_into_protected
b="$(git rev-parse HEAD)"
\git merge --no-ff -m "merge feat/x" feat/x >/dev/null 2>&1; rc=$?
check_commit_blocked "\\git merge --no-ff feat/x into protected" "$rc" "$b"

# ---------------------------------------------------------------------
# DOCUMENTED LIMITATION, BACKSTOPPED — git runs NO commit-time hook for a
# conflict-free cherry-pick/revert replaying a commit onto the current
# branch, so such a commit CAN land on a LOCAL protected branch. That is
# a git behavior, not a hole we can close with another .githooks script.
# We record the local landing as the known limitation (NOT a failure) and
# then assert the backstop that actually holds: pushing that state to the
# protected remote is BLOCKED by pre-push.
# ---------------------------------------------------------------------

# L1: cherry-pick a real (non-empty) commit onto protected, then push.
fresh_repo
git checkout -q feat/x
printf 'cherry\n' > cp_file.txt
git add cp_file.txt
git commit -q -m "content to cherry-pick"
cpsha="$(git rev-parse HEAD)"
git checkout -q -B "$PROTECTED" feat/seed     # protected lacks cp_file.txt
b="$(git rev-parse HEAD)"
git cherry-pick "$cpsha" >/dev/null 2>&1; rc_cp=$?
a="$(git rev-parse HEAD 2>/dev/null || echo none)"
if [ "$rc_cp" -eq 0 ] && [ "$b" != "$a" ]; then
	printf 'NOTE: cherry-pick onto protected landed LOCALLY (rc=0, HEAD advanced) — documented git limitation (no commit-time hook fires); relying on the pre-push backstop below.\n'
else
	printf 'NOTE: cherry-pick onto protected did not land locally (rc=%s) — no weaker than the documented limitation.\n' "$rc_cp"
fi
git push -q origin HEAD >/dev/null 2>&1; rc=$?
check_push_blocked "push of cherry-picked commit on protected is blocked (pre-push backstop)" "$rc"

# L2: revert a real commit on protected, then push.
fresh_repo
git checkout -q feat/x
printf 'revert-me\n' > rv_file.txt
git add rv_file.txt
git commit -q -m "content to revert"
git checkout -q -B "$PROTECTED" feat/x        # protected AT feat/x tip (has rv_file)
b="$(git rev-parse HEAD)"
git revert --no-edit HEAD >/dev/null 2>&1; rc_rv=$?
a="$(git rev-parse HEAD 2>/dev/null || echo none)"
if [ "$rc_rv" -eq 0 ] && [ "$b" != "$a" ]; then
	printf 'NOTE: revert onto protected landed LOCALLY (rc=0, HEAD advanced) — documented git limitation (no commit-time hook fires); relying on the pre-push backstop below.\n'
else
	printf 'NOTE: revert onto protected did not land locally (rc=%s) — no weaker than the documented limitation.\n' "$rc_rv"
fi
git push -q origin HEAD >/dev/null 2>&1; rc=$?
check_push_blocked "push of reverted commit on protected is blocked (pre-push backstop)" "$rc"

# ---------------------------------------------------------------------
# OVER-BLOCK guards — legitimate feature-branch work must still succeed.
# ---------------------------------------------------------------------

# N0: a non-ff merge INTO a feature branch still succeeds (pre-merge-commit
# must not over-block off protected).
fresh_repo
git checkout -q feat/x
git commit -q --allow-empty -m "feat work ahead of seed"
git checkout -q feat/seed
b="$(git rev-parse HEAD)"
git merge --no-ff -m "merge feat/x" feat/x >/dev/null 2>&1; rc=$?
a="$(git rev-parse HEAD 2>/dev/null || echo none)"
if [ "$rc" -eq 0 ] && [ "$b" != "$a" ]; then
	pass "merge --no-ff into feature branch succeeds (no over-block)"
else
	fail "merge --no-ff into feature branch succeeds (no over-block) [rc=$rc before=$b after=$a]"
fi

# N1: a real commit on a feature branch succeeds and advances HEAD
fresh_repo
git checkout -q feat/seed
b="$(git rev-parse HEAD)"
git commit --allow-empty -m ok >/dev/null 2>&1; rc=$?
a="$(git rev-parse HEAD 2>/dev/null || echo none)"
if [ "$rc" -eq 0 ] && [ "$b" != "$a" ]; then
	pass "commit on feature branch succeeds (no over-block)"
else
	fail "commit on feature branch succeeds (no over-block) [rc=$rc before=$b after=$a]"
fi

# N2: a real push of a feature branch succeeds and the ref lands
fresh_repo
git checkout -q feat/seed
git push -q origin HEAD >/dev/null 2>&1; rc=$?
if [ "$rc" -eq 0 ] && git ls-remote --heads origin feat/seed 2>/dev/null | grep -q .; then
	pass "push of feature branch lands in remote (no over-block)"
else
	fail "push of feature branch lands in remote (no over-block) [rc=$rc]"
fi

# N3: a feature branch whose BASENAME collides with a protected name
# (e.g. `release/$PROTECTED`, `dependabot/master`) must NOT be over-blocked.
# The pre-push guard matches the full refs/heads/-stripped ref exactly, so
# `release/main` != `main`. Regression guard for the basename-match defect.
fresh_repo
git checkout -q -b "release/$PROTECTED"
git push -q origin HEAD >/dev/null 2>&1; rc=$?
if [ "$rc" -eq 0 ] && git ls-remote --heads origin "release/$PROTECTED" 2>/dev/null | grep -q .; then
	pass "push of 'release/$PROTECTED' lands (basename does not over-block)"
else
	fail "push of 'release/$PROTECTED' lands (basename does not over-block) [rc=$rc]"
fi

# ---------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------
printf '\n=== summary: %d passed, %d failed, %d skipped ===\n' "$PASS" "$FAIL" "$SKIP"
if [ "$FAIL" -ne 0 ]; then
	echo "RESULT: FAIL"
	exit 1
fi
echo "RESULT: PASS"
exit 0
