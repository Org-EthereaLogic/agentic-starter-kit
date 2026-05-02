"""Regression suite for `.claude/hooks/pre-tool-use.js`.

Each test sets up a temporary git repository on a controlled branch
and invokes the hook with a JSON payload via stdin per the Claude
Code hook protocol. The suite asserts on:

- exit code 0 for allowed payloads.
- exit code 2 for blocked payloads.
- a substring of stderr that names the rejection reason for blocked
  payloads (so a future regression that flips the reason without
  changing the exit code still surfaces).

The eight bypass classes covered are documented in
`.claude/hooks/README.md`. Adding a new test case before patching
the hook is the rule (`README.md` "Discovery protocol").
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HOOK_PATH = REPO_ROOT / ".claude" / "hooks" / "pre-tool-use.js"
FIXTURES = REPO_ROOT / "tests" / "fixtures"

DEFAULT_BRANCH = "{{ cookiecutter.default_branch_name }}"


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


def _bash_payload(command: str) -> str:
    return json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})


def _run_hook(payload: str, cwd: Path) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["node", str(HOOK_PATH)],
        input=payload.encode(),
        capture_output=True,
        cwd=cwd,
    )


class PreToolUseHookTests(unittest.TestCase):
    """Bypass-class regression suite."""

    def test_refspec_to_protected_blocks(self) -> None:
        """Class 2: refspec-to-protected blocks regardless of HEAD."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _setup_repo(tmp_path, "feat/x")
            payload = _bash_payload(
                f"git push origin feat/x:{DEFAULT_BRANCH}"
            )
            result = _run_hook(payload, tmp_path)
        self.assertEqual(result.returncode, 2)
        self.assertIn(DEFAULT_BRANCH, result.stderr.decode())

    def test_implicit_push_from_protected_blocks(self) -> None:
        """Class 1: `git push` with no refspec while HEAD is protected."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _setup_repo(tmp_path, DEFAULT_BRANCH)
            payload = _bash_payload("git push")
            result = _run_hook(payload, tmp_path)
        self.assertEqual(result.returncode, 2)
        self.assertIn(DEFAULT_BRANCH, result.stderr.decode())

    def test_broad_push_all_blocks(self) -> None:
        """Class 4: `--all` blocks regardless of HEAD."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _setup_repo(tmp_path, "feat/x")
            payload = _bash_payload("git push --all origin")
            result = _run_hook(payload, tmp_path)
        self.assertEqual(result.returncode, 2)
        self.assertIn("--all", result.stderr.decode())

    def test_broad_push_mirror_blocks(self) -> None:
        """Class 4: `--mirror` blocks regardless of HEAD."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _setup_repo(tmp_path, "feat/x")
            payload = _bash_payload("git push --mirror origin")
            result = _run_hook(payload, tmp_path)
        self.assertEqual(result.returncode, 2)
        self.assertIn("--mirror", result.stderr.decode())

    def test_commit_on_protected_blocks(self) -> None:
        """Class 5: `git commit` while HEAD is protected."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _setup_repo(tmp_path, DEFAULT_BRANCH)
            payload = _bash_payload("git commit -m 'feat: x'")
            result = _run_hook(payload, tmp_path)
        self.assertEqual(result.returncode, 2)
        self.assertIn("commit", result.stderr.decode().lower())

    def test_merge_on_protected_blocks(self) -> None:
        """Class 6: commit-producing subcommand on protected HEAD."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _setup_repo(tmp_path, DEFAULT_BRANCH)
            payload = _bash_payload("git merge feat/x")
            result = _run_hook(payload, tmp_path)
        self.assertEqual(result.returncode, 2)
        self.assertIn("merge", result.stderr.decode().lower())

    def test_rebase_on_protected_blocks(self) -> None:
        """Class 6: rebase variant of commit-producing subcommand."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _setup_repo(tmp_path, DEFAULT_BRANCH)
            payload = _bash_payload("git rebase feat/x")
            result = _run_hook(payload, tmp_path)
        self.assertEqual(result.returncode, 2)

    def test_nested_shell_blocks(self) -> None:
        """Class 7: `bash -c "git push ..."` is re-evaluated."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _setup_repo(tmp_path, "feat/x")
            payload = _bash_payload(
                f'bash -c "git push origin feat/x:{DEFAULT_BRANCH}"'
            )
            result = _run_hook(payload, tmp_path)
        self.assertEqual(result.returncode, 2)
        self.assertIn("nested", result.stderr.decode().lower())

    def test_chained_subcommand_blocks(self) -> None:
        """Class 8: `&&`-chained git push to protected."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _setup_repo(tmp_path, "feat/x")
            payload = _bash_payload(
                f"true && git push origin feat/x:{DEFAULT_BRANCH}"
            )
            result = _run_hook(payload, tmp_path)
        self.assertEqual(result.returncode, 2)

    def test_feature_branch_push_allows(self) -> None:
        """Baseline: pushing a feature branch to itself is fine."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _setup_repo(tmp_path, "feat/x")
            payload = _bash_payload("git push origin feat/x:feat/x")
            result = _run_hook(payload, tmp_path)
        self.assertEqual(result.returncode, 0)

    def test_feature_branch_commit_allows(self) -> None:
        """Baseline: committing on a feature branch is fine."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _setup_repo(tmp_path, "feat/x")
            payload = _bash_payload("git commit -m 'feat: x'")
            result = _run_hook(payload, tmp_path)
        self.assertEqual(result.returncode, 0)

    def test_non_bash_tool_passes_through(self) -> None:
        """Baseline: non-Bash tool calls are out of scope."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            payload = json.dumps(
                {"tool_name": "Read", "tool_input": {"file_path": "/x"}}
            )
            result = _run_hook(payload, tmp_path)
        self.assertEqual(result.returncode, 0)

    def test_non_git_bash_passes_through(self) -> None:
        """Baseline: non-git Bash commands pass through."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            payload = _bash_payload("ls -la")
            result = _run_hook(payload, tmp_path)
        self.assertEqual(result.returncode, 0)

    def test_empty_command_passes_through(self) -> None:
        """Baseline: empty Bash command is a no-op."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            payload = _bash_payload("")
            result = _run_hook(payload, tmp_path)
        self.assertEqual(result.returncode, 0)


class FixtureSmokeTests(unittest.TestCase):
    """Smoke tests over the fixture files in `tests/fixtures/`.

    These verify that fixtures shipped with the template can be
    invoked directly per `.claude/hooks/README.md` "Ad-hoc invocation".
    """

    def test_protected_push_fixture_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _setup_repo(tmp_path, "feat/x")
            payload = (FIXTURES / "protected-push.json").read_text()
            result = _run_hook(payload, tmp_path)
        self.assertEqual(result.returncode, 2)

    def test_broad_push_all_fixture_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            payload = (FIXTURES / "broad-push-all.json").read_text()
            result = _run_hook(payload, tmp_path)
        self.assertEqual(result.returncode, 2)

    def test_feature_push_fixture_allows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _setup_repo(tmp_path, "feat/x")
            payload = (FIXTURES / "feature-push-allowed.json").read_text()
            result = _run_hook(payload, tmp_path)
        self.assertEqual(result.returncode, 0)

    def test_non_bash_fixture_passes_through(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            payload = (FIXTURES / "non-bash-tool.json").read_text()
            result = _run_hook(payload, tmp_path)
        self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
