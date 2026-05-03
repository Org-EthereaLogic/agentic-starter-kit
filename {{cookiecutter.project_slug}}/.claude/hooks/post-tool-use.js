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

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HOOK_DIR = fileURLToPath(new URL(".", import.meta.url));
const PROJECT_ROOT =
  process.env.CLAUDE_PROJECT_ROOT || path.resolve(HOOK_DIR, "..", "..");
const REPORT_DIR = path.join(PROJECT_ROOT, "report");
const AUDIT_LOG = path.join(REPORT_DIR, "audit.jsonl");
const HOOK_EVENT = process.env.CLAUDE_HOOK_EVENT || null;

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

function firstDefined(...values) {
  for (const value of values) {
    if (value !== undefined && value !== null) {
      return value;
    }
  }
  return null;
}

function firstFiniteNumber(...values) {
  for (const value of values) {
    if (typeof value === "number" && Number.isFinite(value)) {
      return value;
    }
    if (typeof value === "string" && value.trim() !== "") {
      const parsed = Number(value);
      if (Number.isFinite(parsed)) {
        return parsed;
      }
    }
  }
  return null;
}

function inferSuccess(payload, response) {
  const eventName = firstDefined(
    payload.hook_event,
    payload.hook_event_name,
    HOOK_EVENT,
  );
  if (eventName === "PostToolUseFailure") {
    return false;
  }

  const explicitSuccess = firstDefined(response.success, payload.success);
  if (typeof explicitSuccess === "boolean") {
    return explicitSuccess;
  }

  if (firstDefined(response.error, payload.error) !== null) {
    return false;
  }

  const exit = firstFiniteNumber(
    payload.exit,
    payload.exit_code,
    payload.tool_exit,
    response.exit,
    response.exit_code,
    response.code,
    response.status,
  );
  if (exit !== null) {
    return exit === 0;
  }

  return true;
}

function inferExit(payload, response, success) {
  const exit = firstFiniteNumber(
    payload.exit,
    payload.exit_code,
    payload.tool_exit,
    response.exit,
    response.exit_code,
    response.code,
    response.status,
  );
  if (exit !== null) {
    return exit;
  }
  return success ? 0 : null;
}

function inferDurationMs(payload, response) {
  return firstFiniteNumber(
    payload.duration_ms,
    payload.durationMs,
    response.duration_ms,
    response.durationMs,
  );
}

function main() {
  const payload = safeJsonParse(readStdin());
  // Claude Code's PostToolUse / PostToolUseFailure payload may
  // include tool_name, tool_response, session_id, exit, and
  // duration_ms. We log only the audit fields needed to reconstruct
  // the session timeline and avoid storing full tool inputs/outputs.
  const response = payload.tool_response || {};
  const success = inferSuccess(payload, response);

  const event = {
    type: "tool-result",
    ts: new Date().toISOString(),
    session_id: payload.session_id || null,
    tool_name: payload.tool_name || null,
    success,
    exit: inferExit(payload, response, success),
    duration_ms: inferDurationMs(payload, response),
  };
  appendAudit(JSON.stringify(event));
  process.exit(0);
}

main();
