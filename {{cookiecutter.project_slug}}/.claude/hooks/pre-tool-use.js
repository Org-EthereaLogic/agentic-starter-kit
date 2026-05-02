#!/usr/bin/env node
// {{ cookiecutter.project_name }} — Layer 4 runtime hook
//
// Enforces the protected-branch policy declared in DIRECTIVES.md
// CRIT-008: no direct commit on or push to the default branch
// (configured at template-render time) or the literal `master`.
//
// Invoked by Claude Code on `PreToolUse:Bash`. The hook reads the
// proposed Bash command from stdin (Claude Code's hook protocol),
// inspects it for forbidden patterns, and either allows the call
// (exit 0) or blocks it (exit 2 with stderr describing the block).
//
// Why a hard block rather than a prompt: an autonomous subagent
// running with permission prompts disabled would not be stopped
// by an interactive prompt. The hook is the only reliable choke
// point. CRIT-008 calls for the hook to exist AND be exercised by
// a regression suite — see ../../tests/test_pre_tool_use_hook.{py,js}
// for the contract tests.
//
// Bypass classes covered:
//   1. Direct push to a protected branch (refspec or implicit).
//   2. Refspec push that targets a protected branch from any HEAD.
//   3. Broad push modes (`--all`, `--mirror`) from any HEAD.
//   4. Direct commit on a protected branch.
//   5. Commit-producing subcommands (merge, rebase, cherry-pick,
//      revert, am, pull) on a protected branch.
//   6. Nested-shell escapes — `bash -c "..."`, `sh -c "..."`,
//      `zsh -c "..."` — re-evaluated against their inline payload.
//   7. Chained subcommands joined by `&&`, `||`, `;`, or pipes.
//
// New bypass classes get a regression test FIRST, then the patch.
// See ./README.md for the discovery protocol.

"use strict";

const { execSync } = require("node:child_process");

const PROTECTED_BRANCHES = new Set([
  "{{ cookiecutter.default_branch_name }}",
  "master",
]);
const BROAD_PUSH_FLAGS = new Set(["--all", "--mirror"]);
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

// Split a shell command into logical sub-commands at &&, ||, ;, |, and
// newline. Crude but sufficient for the bypass classes the hook
// covers — the hook is not a security boundary, only an
// agentic-runtime guard.
function splitSubcommands(command) {
  return command
    .split(/&&|\|\||;|\||\n/)
    .map((s) => s.trim())
    .filter(Boolean);
}

function tokenize(cmd) {
  return cmd
    .split(/\s+/)
    .map((t) => t.replace(/^['"]|['"]$/g, ""))
    .filter(Boolean);
}

function isGit(tokens) {
  if (tokens.length === 0) return false;
  let i = 0;
  while (i < tokens.length && /^[A-Za-z_][A-Za-z0-9_]*=/.test(tokens[i])) i++;
  return tokens[i] === "git";
}

function gitSubcommand(tokens) {
  let i = 0;
  while (i < tokens.length && /^[A-Za-z_][A-Za-z0-9_]*=/.test(tokens[i])) i++;
  if (tokens[i] !== "git") return "";
  i++;
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
    const dst = (parts[1] !== undefined ? parts[1] : parts[0]).replace(
      /^refs\/heads\//,
      "",
    );
    if (PROTECTED_BRANCHES.has(dst)) {
      return { blocked: true, reason: `refspec targets '${dst}'` };
    }
  }

  // No refspec given → `git push` uses the upstream tracking branch.
  // If HEAD is on a protected branch, that's what gets pushed.
  if (refspecs.length === 0) {
    const branch = currentBranch();
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
  if (PROTECTED_BRANCHES.has(branch)) {
    return { blocked: true, reason: `HEAD is on '${branch}'` };
  }
  return { blocked: false };
}

function commitProducingOnProtected(tokens) {
  const sub = gitSubcommand(tokens);
  if (!COMMIT_PRODUCING_SUBCOMMANDS.has(sub)) return { blocked: false };
  const branch = currentBranch();
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
//   sh   -c "..."   sh   --command '...'
//   zsh  --command=...
function nestedShellInlineCommand(sub) {
  const shellBinary = "(?:bash|sh|zsh)";
  const leadingEnv = "(?:[A-Za-z_][A-Za-z0-9_]*=\\S+\\s+)*";
  const otherFlags = "(?:-[^\\s=]+\\s+)*";

  const quoted = new RegExp(
    `^\\s*${leadingEnv}${shellBinary}\\s+${otherFlags}(?:-c|--command)\\s+(['"])(.*?)\\1\\s*$`,
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
