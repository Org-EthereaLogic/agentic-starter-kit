// Regression suite for the Layer-4 advisory hooks that build the
// session audit trail. TypeScript-path twin of test_audit_hooks.py.
//
// Run via:  node --test tests/test_audit_hooks.js
//
// Each hook reads a JSON payload from stdin, appends a JSON Lines
// event to `report/audit.jsonl`, and exits 0. The tests verify
// exit code, file creation, event shape, and append-only behavior
// across multiple invocations.

import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import {
  existsSync,
  mkdtempSync,
  mkdirSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const __dirname = fileURLToPath(new URL(".", import.meta.url));

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
    .filter((l) => l.trim().length > 0)
    .map((l) => JSON.parse(l));
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
    const r = runHook(
      "session-start.js",
      { session_id: "test-session-1" },
      cwd,
      { projectRoot },
    );
    assert.equal(r.status, 0, r.stderr);
    const events = readAuditLines(projectRoot);
    assert.equal(events.length, 1);
    assert.equal(events[0].type, "session-start");
    assert.equal(events[0].session_id, "test-session-1");
    assert.equal(events[0].cwd, cwd);
    assert.ok(events[0].ts);
    assert.equal(existsSync(path.join(cwd, "report", "audit.jsonl")), false);
  });
});

test("user-prompt-submit hashes the prompt and never logs the text", () => {
  withTempDir((projectRoot) => {
    const secret = "this should not appear in the audit log";
    const r = runHook(
      "user-prompt-submit.js",
      { session_id: "abc", prompt: secret },
      projectRoot,
      { projectRoot },
    );
    assert.equal(r.status, 0, r.stderr);
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
    const r = runHook(
      "post-tool-use.js",
      {
        session_id: "s1",
        tool_name: "Bash",
        tool_response: { success: true, exit: 0, duration_ms: 18 },
      },
      projectRoot,
      { projectRoot, env: { CLAUDE_HOOK_EVENT: "PostToolUse" } },
    );
    assert.equal(r.status, 0, r.stderr);
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
    const r = runHook(
      "post-tool-use.js",
      {
        session_id: "s1",
        tool_name: "Bash",
        tool_response: { exit: 64, duration_ms: 7 },
      },
      projectRoot,
      { projectRoot, env: { CLAUDE_HOOK_EVENT: "PostToolUseFailure" } },
    );
    assert.equal(r.status, 0, r.stderr);
    const events = readAuditLines(projectRoot);
    assert.equal(events[0].success, false);
    assert.equal(events[0].exit, 64);
    assert.equal(events[0].duration_ms, 7);
  });
});

test("audit log is append-only across multiple invocations", () => {
  withTempDir((projectRoot) => {
    runHook("session-start.js", { session_id: "1" }, projectRoot, { projectRoot });
    runHook(
      "user-prompt-submit.js",
      { session_id: "1", prompt: "first" },
      projectRoot,
      { projectRoot },
    );
    runHook(
      "post-tool-use.js",
      { session_id: "1", tool_name: "Bash", tool_response: { success: true } },
      projectRoot,
      { projectRoot, env: { CLAUDE_HOOK_EVENT: "PostToolUse" } },
    );
    const events = readAuditLines(projectRoot);
    assert.equal(events.length, 3);
    assert.deepEqual(
      events.map((e) => e.type),
      ["session-start", "prompt", "tool-result"]
    );
  });
});

test("write failure to report/ does not block the agent runtime", () => {
  withTempDir((projectRoot) => {
    writeFileSync(path.join(projectRoot, "report"), "not a directory");
    const r = runHook("session-start.js", {}, projectRoot, { projectRoot });
    assert.equal(r.status, 0);
    assert.match(r.stderr, /audit-trail write failed/);
  });
});
