#!/usr/bin/env node
// {{ cookiecutter.project_name }} — Layer 4 runtime hook
//
// DEFENSE-IN-DEPTH, NOT THE CRIT-008 GUARANTEE. This hook is a fast,
// agent-facing EARLY block on the protected-branch policy declared in
// DIRECTIVES.md CRIT-008 (no direct commit on or push to the render-
// time default branch or the literal `master`). It inspects the
// proposed command STRING before the shell expands/aliases/word-splits
// it, so shell idioms (eval, exec, `\git`, `git${IFS}push`, `bash -cl`,
// `sudo`/`doas`, `stdbuf`/`setsid`, `&` chains) can defeat it — see
// issue #102. It is therefore best-effort, not the boundary.
//
// THE PRIMARY, ENFORCED CRIT-008 BOUNDARY IS THE GIT-LAYER HOOK:
// ../../.githooks/pre-commit and ../../.githooks/pre-push, installed
// via `git config core.hooksPath .githooks` (`make hooks-install`).
// Those run AFTER shell resolution — git invokes them no matter how the
// command was spelled — so they cannot be dodged by shell syntax. This
// hook's value is speed: it blocks the obvious cases early, in the
// agent's own turn, before a `git` subprocess even starts.
//
// Invoked by Claude Code on `PreToolUse:Bash`. The hook reads the
// proposed Bash command from stdin (Claude Code's hook protocol),
// inspects it for forbidden patterns, and either allows the call
// (exit 0) or blocks it (exit 2 with stderr describing the block).
//
// Why a hard block rather than a prompt: an autonomous subagent
// running with permission prompts disabled would not be stopped
// by an interactive prompt. CRIT-008 calls for the hook to exist AND
// be exercised by a regression suite — see
// ../../tests/test_pre_tool_use_hook.{py,js} for the contract tests,
// and ../../tests/test_git_hooks.sh for the git-layer boundary tests.
//
// Bypass classes covered:
//   1. Direct push to a protected branch (refspec or implicit).
//   2. Refspec push that targets a protected branch from any HEAD.
//   3. Broad push modes (`--all`, `--mirror`, `--branches`) from any
//      HEAD.
//   4. Direct commit on a protected branch.
//   5. Commit-producing subcommands (merge, rebase, cherry-pick,
//      revert, am, pull) on a protected branch.
//   6. Nested-shell escapes — `bash -c "..."`, `sh -c "..."`,
//      `zsh -c "..."` — re-evaluated against their inline payload.
//   7. Chained subcommands joined by `&&`, `||`, `;`, `|`, or `&`.
//
// Bypass classes closed for issue #102 (CRIT-008 hardening):
//   9.  Refspec destination of `HEAD` (or `@`) normalized to the
//       current branch before the protected-set check.
//   10. Single `&` job-control separator treated as a subcommand
//       boundary (not just `&&`).
//   11. Nested-shell combined short-flag clusters — `bash -lc "..."`,
//       `sh -ic "..."` — recognized as `-c` invocations.
//   12. Quoted nested-shell payloads whose inner `;`/`|` no longer
//       fragment the payload before extraction (quote-aware split).
//   13. Trivial command wrappers around git — `env`, `command`,
//       `nice`, `xargs`, `nohup`, `time`, `timeout` — peeled before
//       the git check.
//   14. `--branches` broad push mode (git >= 2.44 synonym of `--all`).
//   15. Fail CLOSED (block) when the current-branch lookup fails for
//       an otherwise-matching git push/commit/commit-producing command.
//   16. Nested-shell short-flag clusters where `-c` is NOT the last
//       letter — `bash -cl "..."`, `sh -ci "..."`, `bash -cx "..."` —
//       recognized as `-c` invocations (ANY single-dash cluster that
//       contains `c`, in any position, not only clusters ending in `c`).
//   17. `sudo` wrapper around git — `sudo git push …`, `sudo -u <user>
//       git push …`, `sudo -n git …` — peeled (with sudo's arg-taking
//       options `-u`/`-g`/`-p`/… consumed) before the git check, while
//       non-git targets (`sudo systemctl restart …`) still pass through.
//
// Bypass classes closed at the merge-family test gate (defense-in-depth
// for the git-layer pre-merge-commit boundary):
//   18. `eval '<payload>'` / `eval "<payload>"` — the quoted payload is
//       extracted and recursively evaluated (like a nested-shell
//       payload), so `eval 'git cherry-pick …'`/`eval "git merge …"` on
//       a protected branch is caught, while read-only (`eval 'git
//       status'`) and non-git (`eval 'npm run build'`) payloads pass.
//   19. Backslash-escaped command token `\git` — a single leading
//       backslash is stripped from the resolved command token before the
//       `isGit`/git-subcommand check, so `\git merge …`/`\git commit …`
//       on a protected branch is caught, while `\git status` off a
//       protected branch stays allowed.
//
// New bypass classes get a regression test FIRST, then the patch.
// See ./README.md for the discovery protocol.

"use strict";

const { execSync } = require("node:child_process");

const PROTECTED_BRANCHES = new Set([
  "{{ cookiecutter.default_branch_name }}",
  "master",
]);
const BROAD_PUSH_FLAGS = new Set(["--all", "--mirror", "--branches"]);
// Trivial command wrappers that run the command that follows them.
// They are peeled off before the `git` check so `env git push …`,
// `nice git push …`, etc. cannot mask a forbidden git command.
const WRAPPER_COMMANDS = new Set([
  "env",
  "command",
  "nice",
  "nohup",
  "time",
  "timeout",
  "xargs",
  "sudo",
]);
// Reason string emitted when the current-branch lookup fails for a
// command that has already matched a forbidden git shape. Kept stable
// so the regression suite can assert on it (check_stderr).
const FAIL_CLOSED_REASON = "could not resolve current branch (fail-closed)";
// Subcommands that produce new commits on HEAD without invoking
// `git commit` directly. If HEAD is on a protected branch, these
// are treated equivalently to `git commit` and blocked under the
// same policy.
const COMMIT_PRODUCING_SUBCOMMANDS = new Set([
  "merge",
  "rebase",
  "cherry-pick",
  "revert",
  "am",
  "pull",
]);
const MAX_NESTED_DEPTH = 4;

function readStdin() {
  try {
    return require("node:fs").readFileSync(0, "utf8");
  } catch (_err) {
    return "";
  }
}

function currentBranch() {
  try {
    return execSync("git rev-parse --abbrev-ref HEAD", {
      encoding: "utf8",
      stdio: ["ignore", "pipe", "ignore"],
    }).trim();
  } catch (_err) {
    return "";
  }
}

// Split a shell command into logical sub-commands at &&, ||, ;, |, &,
// and newline. Quote-aware: a separator inside single or double quotes
// is NOT a split point, so a quoted nested-shell payload stays intact
// and its inner `;`/`|` is only re-split inside the recursive
// evaluate() call after the payload is extracted. Crude but sufficient
// for the bypass classes the hook covers — the hook is not a general
// shell parser, only an agentic-runtime guard.
function splitSubcommands(command) {
  const parts = [];
  let current = "";
  let inSingle = false;
  let inDouble = false;
  for (let i = 0; i < command.length; i++) {
    const ch = command[i];
    if (inSingle) {
      current += ch;
      if (ch === "'") inSingle = false;
      continue;
    }
    if (inDouble) {
      current += ch;
      if (ch === '"') inDouble = false;
      continue;
    }
    if (ch === "'") {
      inSingle = true;
      current += ch;
      continue;
    }
    if (ch === '"') {
      inDouble = true;
      current += ch;
      continue;
    }
    if (ch === "\n" || ch === ";") {
      parts.push(current);
      current = "";
      continue;
    }
    if (ch === "&") {
      parts.push(current);
      current = "";
      if (command[i + 1] === "&") i++; // consume the 2nd '&' of '&&'
      continue;
    }
    if (ch === "|") {
      parts.push(current);
      current = "";
      if (command[i + 1] === "|") i++; // consume the 2nd '|' of '||'
      continue;
    }
    current += ch;
  }
  parts.push(current);
  return parts.map((s) => s.trim()).filter(Boolean);
}

function tokenize(cmd) {
  return cmd
    .split(/\s+/)
    .map((t) => t.replace(/^['"]|['"]$/g, ""))
    .filter(Boolean);
}

// Return the index of the `git` token after skipping leading
// environment assignments (VAR=val) and trivial command wrappers
// (env, command, nice, xargs, nohup, time, timeout, sudo), or -1 if the
// command does not resolve to git. Wrapper option flags and the single
// value that `nice -n` / `timeout -s|-k` / `sudo -u|-g|-p|…` take are
// consumed so they are not mistaken for the wrapped command;
// `timeout <duration>` and env's trailing VAR=val assignments are
// likewise skipped. Loops so stacked wrappers (`env command git …`,
// `env VAR=v nice git …`, `sudo -u ci nice git …`) resolve.
function gitCommandStart(tokens) {
  let i = 0;
  const isAssignment = (t) => /^[A-Za-z_][A-Za-z0-9_]*=/.test(t);
  // A leading backslash on a command token (`\git`, `\sudo`) is a shell
  // idiom that suppresses alias/function resolution; it runs the same
  // binary. Strip a single leading backslash before every command-token
  // comparison so `\git commit …` resolves like `git commit …`.
  const unescape = (t) => (t.charAt(0) === "\\" ? t.slice(1) : t);
  while (i < tokens.length && isAssignment(tokens[i])) i++;
  while (i < tokens.length && WRAPPER_COMMANDS.has(unescape(tokens[i]))) {
    const wrapper = unescape(tokens[i]);
    i++;
    while (i < tokens.length && tokens[i].startsWith("-")) {
      const flag = tokens[i];
      i++;
      const takesValue =
        (wrapper === "nice" && flag === "-n") ||
        (wrapper === "timeout" &&
          ["-s", "--signal", "-k", "--kill-after"].includes(flag)) ||
        // sudo options that consume the following argument. Without this
        // `sudo -u ci git push …` would leave `ci` where `git` is looked
        // for and the wrapper would fail to peel to the git command.
        (wrapper === "sudo" &&
          [
            "-u",
            "--user",
            "-g",
            "--group",
            "-p",
            "--prompt",
            "-C",
            "--close-from",
            "-r",
            "--role",
            "-t",
            "--type",
            "-U",
            "--other-user",
          ].includes(flag));
      if (takesValue && i < tokens.length && !tokens[i].startsWith("-")) i++;
    }
    // `timeout DURATION cmd …` takes a bare leading duration positional.
    if (
      wrapper === "timeout" &&
      i < tokens.length &&
      /^[0-9]/.test(tokens[i])
    ) {
      i++;
    }
    // `env` may be followed by further VAR=val assignments.
    if (wrapper === "env") {
      while (i < tokens.length && isAssignment(tokens[i])) i++;
    }
  }
  return tokens[i] !== undefined && unescape(tokens[i]) === "git" ? i : -1;
}

function isGit(tokens) {
  return gitCommandStart(tokens) !== -1;
}

function gitSubcommand(tokens) {
  const start = gitCommandStart(tokens);
  if (start === -1) return "";
  let i = start + 1;
  while (i < tokens.length && tokens[i].startsWith("-")) {
    if (tokens[i] === "-c" || tokens[i] === "-C") i += 2;
    else i++;
  }
  return tokens[i] || "";
}

function pushTargetsProtected(tokens) {
  const sub = gitSubcommand(tokens);
  if (sub !== "push") return { blocked: false };

  let i = tokens.indexOf("push") + 1;
  const positionals = [];
  while (i < tokens.length) {
    const t = tokens[i];
    if (t.startsWith("-")) {
      if (BROAD_PUSH_FLAGS.has(t)) {
        return {
          blocked: true,
          reason: `broad push mode '${t}' may update protected branches`,
        };
      }
      i++;
      continue;
    }
    positionals.push(t);
    i++;
  }

  // First positional is the remote (default `origin`); the rest are
  // refspecs.
  const refspecs = positionals.slice(1);

  for (const spec of refspecs) {
    const stripped = spec.startsWith("+") ? spec.slice(1) : spec;
    const parts = stripped.split(":");
    let dst = (parts[1] !== undefined ? parts[1] : parts[0]).replace(
      /^refs\/heads\//,
      "",
    );
    // A destination of `HEAD` (or its `@` alias) resolves to whatever
    // branch HEAD points at, so normalize it before the protected-set
    // check. If the lookup fails for this already-matched push, fail
    // closed rather than letting `git push origin HEAD` slip through.
    if (dst === "HEAD" || dst === "@") {
      const branch = currentBranch();
      if (!branch) {
        return { blocked: true, reason: FAIL_CLOSED_REASON };
      }
      dst = branch;
    }
    if (PROTECTED_BRANCHES.has(dst)) {
      return { blocked: true, reason: `refspec targets '${dst}'` };
    }
  }

  // No refspec given → `git push` uses the upstream tracking branch.
  // If HEAD is on a protected branch, that's what gets pushed. A failed
  // branch lookup for this otherwise-matching push fails closed.
  if (refspecs.length === 0) {
    const branch = currentBranch();
    if (!branch) {
      return { blocked: true, reason: FAIL_CLOSED_REASON };
    }
    if (PROTECTED_BRANCHES.has(branch)) {
      return {
        blocked: true,
        reason: `HEAD is on '${branch}' and no explicit refspec was given`,
      };
    }
  }

  return { blocked: false };
}

function commitOnProtected(tokens) {
  const sub = gitSubcommand(tokens);
  if (sub !== "commit") return { blocked: false };
  const branch = currentBranch();
  if (!branch) {
    return { blocked: true, reason: FAIL_CLOSED_REASON };
  }
  if (PROTECTED_BRANCHES.has(branch)) {
    return { blocked: true, reason: `HEAD is on '${branch}'` };
  }
  return { blocked: false };
}

function commitProducingOnProtected(tokens) {
  const sub = gitSubcommand(tokens);
  if (!COMMIT_PRODUCING_SUBCOMMANDS.has(sub)) return { blocked: false };
  const branch = currentBranch();
  if (!branch) {
    return { blocked: true, reason: FAIL_CLOSED_REASON };
  }
  if (PROTECTED_BRANCHES.has(branch)) {
    return {
      blocked: true,
      reason: `'git ${sub}' produces commits and HEAD is on '${branch}'`,
    };
  }
  return { blocked: false };
}

// Pull an inline command string out of a nested-shell invocation
// like `bash -c "git push origin main"`. The whitespace tokenizer
// would split the quoted payload across multiple tokens, so we
// operate on the raw sub-command string and extract the quoted
// payload with a regex. Supports:
//   bash -c "..."   bash -c '...'
//   bash -lc "..."  sh -ic '...'   (combined short-flag clusters)
//   bash -cl "..."  sh -ci '...'   (`c` not last in the cluster)
//   sh   -c "..."   sh   --command '...'
//   zsh  --command=...
function nestedShellInlineCommand(sub) {
  const shellBinary = "(?:bash|sh|zsh)";
  const leadingEnv = "(?:[A-Za-z_][A-Za-z0-9_]*=\\S+\\s+)*";
  const otherFlags = "(?:-[^\\s=]+\\s+)*";
  // Match a single-dash short-flag cluster that CONTAINS `c` in ANY
  // position — `-c`, `-lc`, `-ic` (c last) as well as `-cl`, `-ci`,
  // `-cx`, `-ilc` (c not last) — or the long `--command` form. The
  // single-dash alternative starts with exactly one `-` followed by a
  // run of letters, so a `--` long option (e.g. `--command`) can never
  // be misread as a cluster and keeps its own alternative.
  const commandFlag = "(?:-[A-Za-z]*c[A-Za-z]*|--command)";

  const quoted = new RegExp(
    `^\\s*${leadingEnv}${shellBinary}\\s+${otherFlags}${commandFlag}\\s+(['"])(.*?)\\1\\s*$`,
  );
  const quotedMatch = sub.match(quoted);
  if (quotedMatch) return quotedMatch[2];

  const inline = new RegExp(
    `^\\s*${leadingEnv}${shellBinary}\\s+${otherFlags}--command=(['"]?)(.*?)\\1\\s*$`,
  );
  const inlineMatch = sub.match(inline);
  if (inlineMatch) return inlineMatch[2];

  return null;
}

// Pull the payload out of an `eval` invocation. `eval` concatenates its
// arguments and executes the result in the current shell, so
// `eval 'git cherry-pick x'` runs a real git command that a
// command-string matcher would otherwise miss (the payload is hidden
// inside a quoted argument). Prefer the fully-quoted form
// (`eval '…'` / `eval "…"`); fall back to the bare form
// (`eval git merge …`) by stripping the leading `eval` token. Returns
// the payload string, or null when the sub-command is not an `eval`.
function evalInlineCommand(sub) {
  const quoted = sub.match(/^\s*eval\s+(['"])([\s\S]*)\1\s*$/);
  if (quoted) return quoted[2];
  const bare = sub.match(/^\s*eval\s+(\S[\s\S]*)$/);
  if (bare) return bare[1];
  return null;
}

function evaluate(command, { depth = 0 } = {}) {
  if (depth > MAX_NESTED_DEPTH) return { blocked: false };

  for (const sub of splitSubcommands(command)) {
    const inline = nestedShellInlineCommand(sub);
    if (inline) {
      const inner = evaluate(inline, { depth: depth + 1 });
      if (inner.blocked) {
        return {
          blocked: true,
          command: sub,
          kind: "nested-shell",
          reason: `${inner.reason} (via nested shell)`,
        };
      }
      // Nested-shell payload is safe; fall through to also check the
      // outer token sequence in case it is itself a git command.
    }

    const evalPayload = evalInlineCommand(sub);
    if (evalPayload) {
      const inner = evaluate(evalPayload, { depth: depth + 1 });
      if (inner.blocked) {
        return {
          blocked: true,
          command: sub,
          kind: "eval",
          reason: `${inner.reason} (via eval)`,
        };
      }
      // eval payload is safe; fall through to also check the outer token
      // sequence (the bare `eval git …` form is handled by the recursive
      // call above, but a non-git eval still passes through here).
    }

    const tokens = tokenize(sub);
    if (!isGit(tokens)) continue;

    const push = pushTargetsProtected(tokens);
    if (push.blocked) {
      return {
        blocked: true,
        command: sub,
        kind: "push",
        reason: push.reason,
      };
    }

    const commit = commitOnProtected(tokens);
    if (commit.blocked) {
      return {
        blocked: true,
        command: sub,
        kind: "commit",
        reason: commit.reason,
      };
    }

    const mergeLike = commitProducingOnProtected(tokens);
    if (mergeLike.blocked) {
      return {
        blocked: true,
        command: sub,
        kind: "merge-like",
        reason: mergeLike.reason,
      };
    }
  }
  return { blocked: false };
}

function main() {
  const raw = readStdin();
  if (!raw) process.exit(0);

  let payload;
  try {
    payload = JSON.parse(raw);
  } catch (_err) {
    process.exit(0);
  }

  if (payload.tool_name !== "Bash") process.exit(0);

  const command = payload?.tool_input?.command;
  if (typeof command !== "string" || command.length === 0) process.exit(0);

  const verdict = evaluate(command);
  if (!verdict.blocked) process.exit(0);

  const message =
    `[{{ cookiecutter.project_slug }}/pre-tool-use] Blocked ${verdict.kind} to a protected branch.\n` +
    `  Sub-command: ${verdict.command}\n` +
    `  Reason: ${verdict.reason}\n\n` +
    `Policy (DIRECTIVES.md CRIT-008): no direct commit on or push to\n` +
    `'{{ cookiecutter.default_branch_name }}' or 'master'. Create a feat/fix/chore branch,\n` +
    `commit there, push the branch, and open a PR.\n\n` +
    `Fix:\n` +
    `  git checkout -b <type>/<slug>\n` +
    `then retry. To temporarily disable for an emergency, edit\n` +
    `.claude/settings.json and acknowledge the deviation in a sync\n` +
    `record under report/.`;

  process.stderr.write(message + "\n");
  process.exit(2);
}

main();
