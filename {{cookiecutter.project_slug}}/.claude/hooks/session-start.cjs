#!/usr/bin/env node
// session-start.cjs — Layer 4 advisory hook for {{ cookiecutter.project_name }}
//
// Invoked by Claude Code on `SessionStart`. Appends a JSON Lines
// event to `report/audit.jsonl` recording the session boundary so
// the entire session is reconstructable later. Always exits 0; this
// hook is advisory, not gating.
//
// Audit-trail policy: appends only, never edits or deletes earlier
// lines (per `IMP-001` — append-only `report/`). Each hook handles
// its own write failures gracefully — a broken audit trail must
// not break the agent runtime.

"use strict";

const fs = require("node:fs");
const path = require("node:path");
const { execSync } = require("node:child_process");

const PROJECT_ROOT =
  process.env.CLAUDE_PROJECT_ROOT || path.resolve(__dirname, "..", "..");
const REPORT_DIR = path.join(PROJECT_ROOT, "report");
const AUDIT_LOG = path.join(REPORT_DIR, "audit.jsonl");

function readStdin() {
  try {
    return fs.readFileSync(0, "utf8");
  } catch (_err) {
    return "";
  }
}

function safeJsonParse(text) {
  try {
    return JSON.parse(text || "{}");
  } catch (_err) {
    return {};
  }
}

function getGitHead() {
  try {
    return execSync("git rev-parse HEAD", {
      cwd: PROJECT_ROOT,
      encoding: "utf8",
      stdio: ["ignore", "pipe", "ignore"],
    }).trim();
  } catch (_err) {
    return null;
  }
}

function appendAudit(line) {
  try {
    fs.mkdirSync(REPORT_DIR, { recursive: true });
    fs.appendFileSync(AUDIT_LOG, line + "\n");
  } catch (err) {
    process.stderr.write(`audit-trail write failed: ${err.message}\n`);
  }
}

function main() {
  const payload = safeJsonParse(readStdin());
  const event = {
    type: "session-start",
    ts: new Date().toISOString(),
    cwd: process.cwd(),
    git_head: getGitHead(),
    session_id: payload.session_id || null,
    transcript_path: payload.transcript_path || null,
  };
  appendAudit(JSON.stringify(event));
  process.exit(0);
}

main();