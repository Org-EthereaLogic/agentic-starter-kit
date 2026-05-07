// Regression suite for `.claude/hooks/pre-tool-use.js`.
//
// Driven by `tests/hook_test_spec.json` — the single source of truth
// shared with `test_pre_tool_use_hook.py`. Each scenario in the spec
// is dispatched as one `node:test` test at module load.
//
// Uses Node 20+'s built-in `node:test` runner — no external test
// framework required. Each test sets up a temporary git repo on the
// scenario's branch (when specified) and invokes the hook with a JSON
// payload via stdin per the Claude Code hook protocol.
//
// The eight bypass classes covered are documented in
// `.claude/hooks/README.md`.

import test from "node:test";
import assert from "node:assert/strict";
import { execFileSync, spawnSync } from "node:child_process";
import { mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = fileURLToPath(new URL(".", import.meta.url));

const REPO_ROOT = path.resolve(__dirname, "..");
const HOOK_PATH = path.join(REPO_ROOT, ".claude", "hooks", "pre-tool-use.js");
const FIXTURES = path.join(REPO_ROOT, "tests", "fixtures");
const SPEC_PATH = path.join(REPO_ROOT, "tests", "hook_test_spec.json");
const SPEC = JSON.parse(readFileSync(SPEC_PATH, "utf8"));

function gitEnv() {
  return {
    ...process.env,
    GIT_AUTHOR_NAME: "test",
    GIT_AUTHOR_EMAIL: "test@example.invalid",
    GIT_COMMITTER_NAME: "test",
    GIT_COMMITTER_EMAIL: "test@example.invalid",
    GIT_CONFIG_GLOBAL: "/dev/null",
    GIT_CONFIG_SYSTEM: "/dev/null",
  };
}

function setupRepo(branch) {
  const dir = mkdtempSync(path.join(tmpdir(), "hook-test-"));
  const env = gitEnv();
  execFileSync("git", ["init", "-q", "-b", branch], { cwd: dir, env });
  writeFileSync(path.join(dir, "seed.txt"), "seed\n");
  execFileSync("git", ["add", "seed.txt"], { cwd: dir, env });
  execFileSync("git", ["commit", "-q", "-m", "seed"], { cwd: dir, env });
  return dir;
}

function runHook(payload, cwd) {
  return spawnSync("node", [HOOK_PATH], {
    input: payload,
    cwd,
    encoding: "utf8",
  });
}

function payloadFor(scenario) {
  if (scenario.fixture) {
    return readFileSync(path.join(FIXTURES, scenario.fixture), "utf8");
  }
  if (scenario.tool_name) {
    return JSON.stringify({
      tool_name: scenario.tool_name,
      tool_input: scenario.tool_input || {},
    });
  }
  return JSON.stringify({
    tool_name: "Bash",
    tool_input: { command: scenario.command || "" },
  });
}

function runScenario(scenario) {
  const dir = scenario.branch
    ? setupRepo(scenario.branch)
    : mkdtempSync(path.join(tmpdir(), "hook-test-"));
  const result = runHook(payloadFor(scenario), dir);
  assert.equal(
    result.status,
    scenario.expected_exit,
    `${scenario.name}: expected exit ${scenario.expected_exit}, got ${result.status}; stderr=${JSON.stringify(result.stderr)}`,
  );
  if (scenario.check_stderr) {
    const needle = scenario.check_stderr.toLowerCase();
    assert.ok(
      String(result.stderr).toLowerCase().includes(needle),
      `${scenario.name}: stderr did not contain ${JSON.stringify(scenario.check_stderr)}; stderr=${JSON.stringify(result.stderr)}`,
    );
  }
}

for (const scenario of [...SPEC.tests, ...SPEC.fixtures]) {
  test(scenario.description || scenario.name, () => runScenario(scenario));
}
