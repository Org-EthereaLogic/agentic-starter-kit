#!/usr/bin/env node
// post-tool-use.js — Layer 4 advisory hook for {{ cookiecutter.project_name }}
//
// Invoked by Claude Code on `PostToolUse`. Records a per-tool-call
// summary in `report/audit.jsonl` so the session timeline includes
// what the agent ran and whether it succeeded. The summary records
// the tool name and exit status; it does NOT record tool inputs or
// outputs, which can be large and may contain sensitive data.
//
// Always exits 0; advisory hook.

"use strict";

const fs = require("node:fs");
const path = require("node:path");

const REPORT_DIR = path.join(process.cwd(), "report");
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
  // Claude Code's PostToolUse payload may include: tool_name,
  // tool_input, tool_response (with success/error indicators), and
  // session_id. We log a minimal summary — name and outcome — and
  // skip the full input/output to keep the trail compact and free
  // of sensitive content.
  const response = payload.tool_response || {};
  const success = response.success !== false; // default true if absent

  const event = {
    type: "tool-result",
    ts: new Date().toISOString(),
    session_id: payload.session_id || null,
    tool_name: payload.tool_name || null,
    success: success,
  };
  appendAudit(JSON.stringify(event));
  process.exit(0);
}

main();
