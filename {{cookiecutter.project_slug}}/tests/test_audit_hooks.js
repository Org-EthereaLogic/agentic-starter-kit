// Regression suite for the Layer-4 advisory hooks that build the
// session audit trail. TypeScript-path twin of test_audit_hooks.py.
//
// Run via:  node --test tests/test_audit_hooks.js
//
// Each hook reads a JSON payload from stdin, appends a JSON Lines
// event to `report/audit.jsonl`, and exits 0. The tests verify
// exit code, file creation, event shape, and append-only behavior
// across multiple invocations.

"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const { spawnSync } = require("node:child_process");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const REPO_ROOT = path.resolve(__dirname, "..");
const HOOKS_DIR = path.join(REPO_ROOT, ".claude", "hooks");

function runHook(hookFilename, payload, cwd) {
  return spawnSync("node", [path.join(HOOKS_DIR, hookFilename)], {
    input: JSON.stringify(payload),
    cwd,
    encoding: "utf8",
  });
}

function readAuditLines(cwd) {
  const audit = path.join(cwd, "report", "audit.jsonl");
  if (!fs.existsSync(audit)) return [];
  return fs
    .readFileSync(audit, "utf8")
    .split("\n")
    .filter((l) => l.trim().length > 0)
    .map((l) => JSON.parse(l));
}

function withTempDir(fn) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "audit-hooks-"));
  try {
    return fn(dir);
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
}

test("session-start emits session-start event", () => {
  withTempDir((cwd) => {
    const r = runHook("session-start.js", { session_id: "test-session-1" }, cwd);
    assert.equal(r.status, 0, r.stderr);
    const events = readAuditLines(cwd);
    assert.equal(events.length, 1);
    assert.equal(events[0].type, "session-start");
    assert.equal(events[0].session_id, "test-session-1");
    assert.ok(events[0].ts);
    assert.ok(events[0].cwd);
  });
});

test("user-prompt-submit hashes the prompt and never logs the text", () => {
  withTempDir((cwd) => {
    const secret = "this should not appear in the audit log";
    const r = runHook(
      "user-prompt-submit.js",
      { session_id: "abc", prompt: secret },
      cwd
    );
    assert.equal(r.status, 0, r.stderr);
    const audit = fs.readFileSync(path.join(cwd, "report", "audit.jsonl"), "utf8");
    assert.ok(!audit.includes(secret), "prompt text leaked into audit");
    const events = readAuditLines(cwd);
    assert.equal(events[0].type, "prompt");
    assert.match(events[0].prompt_hash, /^sha256:/);
    assert.equal(events[0].prompt_length, secret.length);
  });
});

test("post-tool-use records tool name and success flag", () => {
  withTempDir((cwd) => {
    const r = runHook(
      "post-tool-use.js",
      { session_id: "s1", tool_name: "Bash", tool_response: { success: true } },
      cwd
    );
    assert.equal(r.status, 0, r.stderr);
    const events = readAuditLines(cwd);
    assert.equal(events[0].type, "tool-result");
    assert.equal(events[0].tool_name, "Bash");
    assert.equal(events[0].success, true);
  });
});

test("audit log is append-only across multiple invocations", () => {
  withTempDir((cwd) => {
    runHook("session-start.js", { session_id: "1" }, cwd);
    runHook("user-prompt-submit.js", { session_id: "1", prompt: "first" }, cwd);
    runHook("post-tool-use.js", { session_id: "1", tool_name: "Bash" }, cwd);
    const events = readAuditLines(cwd);
    assert.equal(events.length, 3);
    assert.deepEqual(
      events.map((e) => e.type),
      ["session-start", "prompt", "tool-result"]
    );
  });
});

test("write failure to report/ does not block the agent runtime", () => {
  withTempDir((cwd) => {
    fs.writeFileSync(path.join(cwd, "report"), "not a directory");
    const r = runHook("session-start.js", {}, cwd);
    assert.equal(r.status, 0);
    assert.match(r.stderr, /audit-trail write failed/);
  });
});
