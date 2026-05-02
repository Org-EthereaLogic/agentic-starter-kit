// Regression suite for `.claude/hooks/pre-tool-use.js`.
//
// TypeScript-path equivalent of `tests/test_pre_tool_use_hook.py`.
// Uses Node 20+'s built-in `node:test` runner — no external test
// framework required. Each test sets up a temporary git repo on a
// controlled branch and invokes the hook with a JSON payload via
// stdin per the Claude Code hook protocol.
//
// The eight bypass classes covered are documented in
// `.claude/hooks/README.md`.

"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const { execFileSync, spawnSync } = require("node:child_process");
const { mkdtempSync, readFileSync, writeFileSync } = require("node:fs");
const { tmpdir } = require("node:os");
const path = require("node:path");

const REPO_ROOT = path.resolve(__dirname, "..");
const HOOK_PATH = path.join(REPO_ROOT, ".claude", "hooks", "pre-tool-use.js");
const FIXTURES = path.join(REPO_ROOT, "tests", "fixtures");
const DEFAULT_BRANCH = "{{ cookiecutter.default_branch_name }}";

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

function bashPayload(command) {
  return JSON.stringify({ tool_name: "Bash", tool_input: { command } });
}

function runHook(payload, cwd) {
  return spawnSync("node", [HOOK_PATH], {
    input: payload,
    cwd,
    encoding: "utf8",
  });
}

test("refspec to protected blocks", () => {
  const dir = setupRepo("feat/x");
  const result = runHook(
    bashPayload(`git push origin feat/x:${DEFAULT_BRANCH}`),
    dir,
  );
  assert.equal(result.status, 2);
  assert.match(result.stderr, new RegExp(DEFAULT_BRANCH));
});

test("implicit push from protected blocks", () => {
  const dir = setupRepo(DEFAULT_BRANCH);
  const result = runHook(bashPayload("git push"), dir);
  assert.equal(result.status, 2);
  assert.match(result.stderr, new RegExp(DEFAULT_BRANCH));
});

test("broad push --all blocks", () => {
  const dir = setupRepo("feat/x");
  const result = runHook(bashPayload("git push --all origin"), dir);
  assert.equal(result.status, 2);
  assert.match(result.stderr, /--all/);
});

test("broad push --mirror blocks", () => {
  const dir = setupRepo("feat/x");
  const result = runHook(bashPayload("git push --mirror origin"), dir);
  assert.equal(result.status, 2);
  assert.match(result.stderr, /--mirror/);
});

test("commit on protected blocks", () => {
  const dir = setupRepo(DEFAULT_BRANCH);
  const result = runHook(bashPayload("git commit -m 'feat: x'"), dir);
  assert.equal(result.status, 2);
  assert.match(result.stderr, /commit/i);
});

test("merge on protected blocks", () => {
  const dir = setupRepo(DEFAULT_BRANCH);
  const result = runHook(bashPayload("git merge feat/x"), dir);
  assert.equal(result.status, 2);
  assert.match(result.stderr, /merge/i);
});

test("rebase on protected blocks", () => {
  const dir = setupRepo(DEFAULT_BRANCH);
  const result = runHook(bashPayload("git rebase feat/x"), dir);
  assert.equal(result.status, 2);
});

test("nested shell blocks", () => {
  const dir = setupRepo("feat/x");
  const result = runHook(
    bashPayload(`bash -c "git push origin feat/x:${DEFAULT_BRANCH}"`),
    dir,
  );
  assert.equal(result.status, 2);
  assert.match(result.stderr, /nested/i);
});

test("chained subcommand blocks", () => {
  const dir = setupRepo("feat/x");
  const result = runHook(
    bashPayload(`true && git push origin feat/x:${DEFAULT_BRANCH}`),
    dir,
  );
  assert.equal(result.status, 2);
});

test("feature branch push allows", () => {
  const dir = setupRepo("feat/x");
  const result = runHook(bashPayload("git push origin feat/x:feat/x"), dir);
  assert.equal(result.status, 0);
});

test("feature branch commit allows", () => {
  const dir = setupRepo("feat/x");
  const result = runHook(bashPayload("git commit -m 'feat: x'"), dir);
  assert.equal(result.status, 0);
});

test("non-Bash tool passes through", () => {
  const dir = setupRepo("feat/x");
  const result = runHook(
    JSON.stringify({ tool_name: "Read", tool_input: { file_path: "/x" } }),
    dir,
  );
  assert.equal(result.status, 0);
});

test("non-git Bash command passes through", () => {
  const dir = setupRepo("feat/x");
  const result = runHook(bashPayload("ls -la"), dir);
  assert.equal(result.status, 0);
});

test("empty command passes through", () => {
  const dir = setupRepo("feat/x");
  const result = runHook(bashPayload(""), dir);
  assert.equal(result.status, 0);
});

test("fixture: protected-push.json blocks", () => {
  const dir = setupRepo("feat/x");
  const payload = readFileSync(
    path.join(FIXTURES, "protected-push.json"),
    "utf8",
  );
  const result = runHook(payload, dir);
  assert.equal(result.status, 2);
});

test("fixture: broad-push-all.json blocks", () => {
  const dir = setupRepo("feat/x");
  const payload = readFileSync(
    path.join(FIXTURES, "broad-push-all.json"),
    "utf8",
  );
  const result = runHook(payload, dir);
  assert.equal(result.status, 2);
});

test("fixture: feature-push-allowed.json allows", () => {
  const dir = setupRepo("feat/x");
  const payload = readFileSync(
    path.join(FIXTURES, "feature-push-allowed.json"),
    "utf8",
  );
  const result = runHook(payload, dir);
  assert.equal(result.status, 0);
});

test("fixture: non-bash-tool.json passes through", () => {
  const dir = setupRepo("feat/x");
  const payload = readFileSync(
    path.join(FIXTURES, "non-bash-tool.json"),
    "utf8",
  );
  const result = runHook(payload, dir);
  assert.equal(result.status, 0);
});
