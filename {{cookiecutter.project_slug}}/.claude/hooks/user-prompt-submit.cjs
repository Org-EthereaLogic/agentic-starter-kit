#!/usr/bin/env node
// user-prompt-submit.cjs — Layer 4 advisory hook for {{ cookiecutter.project_name }}
//
// Invoked by Claude Code on `UserPromptSubmit`. Records a SHA-256
// hash of the operator's prompt (NOT the prompt text) in
// `report/audit.jsonl`. The hash supports later forensic analysis
// — "did the operator ask for X in this session" — without leaking
// prompt content into the evidence trail.
//
// Always exits 0; advisory hook.

"use strict";

const crypto = require("node:crypto");
const fs = require("node:fs");
const path = require("node:path");

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
  const prompt = typeof payload.prompt === "string" ? payload.prompt : "";
  const promptHash = "sha256:" + crypto.createHash("sha256").update(prompt).digest("hex");

  const event = {
    type: "prompt",
    ts: new Date().toISOString(),
    session_id: payload.session_id || null,
    prompt_hash: promptHash,
    prompt_length: prompt.length,
  };
  appendAudit(JSON.stringify(event));
  process.exit(0);
}

main();