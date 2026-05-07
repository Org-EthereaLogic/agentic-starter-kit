"""Regression suite for `.claude/hooks/pre-tool-use.js`.

Driven by `tests/hook_test_spec.json` — the single source of truth
shared with `test_pre_tool_use_hook.js`. Each scenario in the spec is
attached to `PreToolUseHookTests` as a `test_<name>` method at import
time, so the standard `python -m unittest tests.test_pre_tool_use_hook
.PreToolUseHookTests.test_<name>` selector still works.

Each test sets up a temporary git repo on the scenario's branch (when
specified) and invokes the hook with a JSON payload via stdin per the
Claude Code hook protocol. Assertions cover:

- exit code 0 for allowed payloads.
- exit code 2 for blocked payloads.
- a case-insensitive substring of stderr that names the rejection
  reason for blocked payloads (so a future regression that flips the
  reason without changing the exit code still surfaces).

The eight bypass classes covered are documented in
`.claude/hooks/README.md`. Adding a new test case to the spec before
patching the hook is the rule (`README.md` "Discovery protocol").
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parent.parent
HOOK_PATH = REPO_ROOT / ".claude" / "hooks" / "pre-tool-use.js"
FIXTURES = REPO_ROOT / "tests" / "fixtures"
SPEC_PATH = REPO_ROOT / "tests" / "hook_test_spec.json"
SPEC = json.loads(SPEC_PATH.read_text())


def _git_env() -> dict[str, str]:
    return {
        **os.environ,
        "GIT_AUTHOR_NAME": "test",
        "GIT_AUTHOR_EMAIL": "test@example.invalid",
        "GIT_COMMITTER_NAME": "test",
        "GIT_COMMITTER_EMAIL": "test@example.invalid",
        # Suppress the global hint about default-branch naming.
        "GIT_CONFIG_GLOBAL": "/dev/null",
        "GIT_CONFIG_SYSTEM": "/dev/null",
    }


def _setup_repo(directory: Path, branch: str) -> None:
    """Initialize a minimal git repo on `branch` with one commit."""
    env = _git_env()
    subprocess.run(
        ["git", "init", "-q", "-b", branch],
        cwd=directory,
        env=env,
        check=True,
    )
    seed = directory / "seed.txt"
    seed.write_text("seed\n")
    subprocess.run(["git", "add", "seed.txt"], cwd=directory, env=env, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "seed"],
        cwd=directory,
        env=env,
        check=True,
    )


def _run_hook(payload: str, cwd: Path) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["node", str(HOOK_PATH)],
        input=payload.encode(),
        capture_output=True,
        cwd=cwd,
    )


def _payload_for(scenario: dict[str, Any]) -> str:
    """Build the JSON payload string for a spec scenario."""
    if "fixture" in scenario:
        return (FIXTURES / scenario["fixture"]).read_text()
    if "tool_name" in scenario:
        body: dict[str, Any] = {
            "tool_name": scenario["tool_name"],
            "tool_input": scenario.get("tool_input", {}),
        }
    else:
        body = {
            "tool_name": "Bash",
            "tool_input": {"command": scenario.get("command", "")},
        }
    return json.dumps(body)


def _make_test(scenario: dict[str, Any]) -> Callable[[unittest.TestCase], None]:
    def test(self: unittest.TestCase) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            branch = scenario.get("branch")
            if branch:
                _setup_repo(tmp_path, branch)
            payload = _payload_for(scenario)
            result = _run_hook(payload, tmp_path)
        stderr = result.stderr.decode()
        self.assertEqual(
            result.returncode,
            scenario["expected_exit"],
            msg=f"{scenario['name']}: expected exit {scenario['expected_exit']}, "
            f"got {result.returncode}; stderr={stderr!r}",
        )
        check = scenario.get("check_stderr")
        if check:
            self.assertIn(
                check.lower(),
                stderr.lower(),
                msg=f"{scenario['name']}: stderr did not contain {check!r}: {stderr!r}",
            )

    test.__doc__ = scenario.get("description", scenario["name"])
    return test


class PreToolUseHookTests(unittest.TestCase):
    """Bypass-class regression suite, driven by hook_test_spec.json."""


for _scenario in [*SPEC.get("tests", []), *SPEC.get("fixtures", [])]:
    setattr(
        PreToolUseHookTests,
        f"test_{_scenario['name']}",
        _make_test(_scenario),
    )


if __name__ == "__main__":
    unittest.main()
