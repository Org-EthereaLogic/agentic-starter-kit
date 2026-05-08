// Regression suite for the Layer-4 advisory hooks that build the
// session audit trail. TypeScript-path twin of test_audit_hooks.py.
//
// Run via:  node --test tests/test_audit_hooks.cjs
//
// Each hook reads a JSON payload from stdin, appends a JSON Lines
// event to `report/audit.jsonl`, and exits 0. The tests verify
// exit code, file creation, event shape, and append-only behavior
// across multiple invocations.

"use strict";

const assert = require("node:assert/strict");
const { spawnSync } = require("node:child_process");
const {
  existsSync,
  mkdtempSync,
  mkdirSync,
  readFileSync,
  realpathSync,
  rmSync,
  writeFileSync,
} = require("node:fs");
const { tmpdir } = require("node:os");
const path = require("node:path");
const test = require("node:test");

const REPO_ROOT = path.resolve(__dirname, "..");
const HOOKS_DIR = path.join(REPO_ROOT, ".claude", "hooks");

function runHook(hookFilename, payload, cwd, { projectRoot = cwd, env = {} } = {}) {
  return spawnSync("node", [path.join(HOOKS_DIR, hookFilename)], {
    input: JSON.stringify(payload),
    cwd,
    encoding: "utf8",
    env: {
      ...process.env,
      CLAUDE_PROJECT_ROOT: projectRoot,
      ...env,
    },
  });
}

function readAuditLines(projectRoot) {
  const audit = path.join(projectRoot, "report", "audit.jsonl");
  if (!existsSync(audit)) return [];
  return readFileSync(audit, "utf8")
    .split("\n")
    .filter((line) => line.trim().length > 0)
    .map((line) => JSON.parse(line));
}

function withTempDir(fn) {
  const dir = mkdtempSync(path.join(tmpdir(), "audit-hooks-"));
  try {
    return fn(dir);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
}

test("session-start anchors audit log to project root", () => {
  withTempDir((projectRoot) => {
    const cwd = path.join(projectRoot, "nested", "workspace");
    mkdirSync(cwd, { recursive: true });
    const result = runHook(
      "session-start.cjs",
      { session_id: "test-session-1" },
      cwd,
      { projectRoot },
    );
    assert.equal(result.status, 0, result.stderr);
    const events = readAuditLines(projectRoot);
    assert.equal(events.length, 1);
    assert.equal(events[0].type, "session-start");
    assert.equal(events[0].session_id, "test-session-1");
    // Node's `process.cwd()` returns the realpath-resolved path on
    // macOS (where `/var` is a symlink to `/private/var`), so compare
    // resolved paths on both sides for cross-platform parity. Linux
    // is unaffected; macOS would otherwise fail. Mirrors the comment
    // and assertion in the Python twin (tests/test_audit_hooks.py).
    assert.equal(events[0].cwd, realpathSync(cwd));
    assert.ok(events[0].ts);
    assert.equal(existsSync(path.join(cwd, "report", "audit.jsonl")), false);
  });
});

test("user-prompt-submit hashes the prompt and never logs the text", () => {
  withTempDir((projectRoot) => {
    const secret = "this should not appear in the audit log";
    const result = runHook(
      "user-prompt-submit.cjs",
      { session_id: "abc", prompt: secret },
      projectRoot,
      { projectRoot },
    );
    assert.equal(result.status, 0, result.stderr);
    const audit = readFileSync(
      path.join(projectRoot, "report", "audit.jsonl"),
      "utf8",
    );
    assert.ok(!audit.includes(secret), "prompt text leaked into audit");
    const events = readAuditLines(projectRoot);
    assert.equal(events[0].type, "prompt");
    assert.match(events[0].prompt_hash, /^sha256:/);
    assert.equal(events[0].prompt_length, secret.length);
  });
});

test("post-tool-use records tool name, success, exit, and duration", () => {
  withTempDir((projectRoot) => {
    const result = runHook(
      "post-tool-use.cjs",
      {
        session_id: "s1",
        tool_name: "Bash",
        tool_response: { success: true, exit: 0, duration_ms: 18 },
      },
      projectRoot,
      { projectRoot, env: { CLAUDE_HOOK_EVENT: "PostToolUse" } },
    );
    assert.equal(result.status, 0, result.stderr);
    const events = readAuditLines(projectRoot);
    assert.equal(events[0].type, "tool-result");
    assert.equal(events[0].tool_name, "Bash");
    assert.equal(events[0].success, true);
    assert.equal(events[0].exit, 0);
    assert.equal(events[0].duration_ms, 18);
  });
});

test("post-tool-use records failed tool calls from failure hook", () => {
  withTempDir((projectRoot) => {
    const result = runHook(
      "post-tool-use.cjs",
      {
        session_id: "s1",
        tool_name: "Bash",
        tool_response: { exit: 64, duration_ms: 7 },
      },
      projectRoot,
      { projectRoot, env: { CLAUDE_HOOK_EVENT: "PostToolUseFailure" } },
    );
    assert.equal(result.status, 0, result.stderr);
    const events = readAuditLines(projectRoot);
    assert.equal(events[0].success, false);
    assert.equal(events[0].exit, 64);
    assert.equal(events[0].duration_ms, 7);
  });
});

test("audit log is append-only across multiple invocations", () => {
  withTempDir((projectRoot) => {
    runHook("session-start.cjs", { session_id: "1" }, projectRoot, { projectRoot });
    runHook(
      "user-prompt-submit.cjs",
      { session_id: "1", prompt: "first" },
      projectRoot,
      { projectRoot },
    );
    runHook(
      "post-tool-use.cjs",
      { session_id: "1", tool_name: "Bash", tool_response: { success: true } },
      projectRoot,
      { projectRoot, env: { CLAUDE_HOOK_EVENT: "PostToolUse" } },
    );
    const events = readAuditLines(projectRoot);
    assert.equal(events.length, 3);
    assert.deepEqual(
      events.map((event) => event.type),
      ["session-start", "prompt", "tool-result"],
    );
  });
});

test("write failure to report/ does not block the agent runtime", () => {
  withTempDir((projectRoot) => {
    writeFileSync(path.join(projectRoot, "report"), "not a directory");
    const result = runHook("session-start.cjs", {}, projectRoot, { projectRoot });
    assert.equal(result.status, 0);
    assert.match(result.stderr, /audit-trail write failed/);
  });
});